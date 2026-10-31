# Q130(a) — the kinds-of-numbers inventory, from what is already measured

*Sat 31 Oct 2026 (week 44), desk lane of Q130, on the Intel. **No card was touched.** Every number here is
read out of a committed file by [`build_inventory.py`](build_inventory.py); the five that have no
machine-readable form are typed into that script's `TYPED` dict with a citation and are marked ᵗ wherever
they appear. Built for the follow-up blog post to Horace He's result — the table the post will quote, and
the list of holes the card lanes of this workflow fill.*

## Results

**fifty-two (format, kind) rows exist across the campaigns, and they are a very uneven table.** 1,166
operand-kind cells and 239 bit-level cells are already measured, modelled or predicted; the whole thing is in
[`inventory.json`](inventory.json) and laid out in [`tables.md`](tables.md).

**Five findings a reader of the inventory should take away before the blog is written.**

1. **The kinds ladder is fp32's alone.** fp32 has **46 kinds**; fp16 and int8 have **three each** — zeros, ones,
   random normal — plus one TenB variant. Both of the formats a reader would actually run inference in are a
   three-point line. That is E78's and E79's whole reason to exist.

2. **Power is measured almost everywhere; SPEED is measured almost nowhere.** `switching_W` exists for 53 rows
   and `pJ_per_MAC` for 50. `sustained_MHz`, `die_C_sustained` and `limit_sustained` exist for **nine** —
   E64's SUS block, three kinds × three formats. Seven fp32 ladder kinds have a cool-die burst clock and no
   sustained cell at all. The blog's headline distinction (burst = the power test, sustained = the thermal test)
   is the part of the table with the fewest cells in it.

3. **The two ends of the chain disagree about what "data-dependent" means.** In the multiply-add, what costs is
   **transitions**: the same 4,096 multiply-adds presented in max-flip rather than Gray order cost
   +0.682 ± 0.010 W more on aifoundry3 and +1.291 ± 0.009 W on aifoundry2, for identical results. On the DRAM
   path, what costs is **carried ones**: 3.255 pJ per one in flight [2.97, 3.55] against nothing measurable per
   changed bit at L1 (−0.0001 pJ), and 94% of the 1,008 pJ per 64 B line that the two designed counts explain is
   the ones term. **So on chip the lever is "reduce transitions" and off chip it is "pack zeros", and they are
   different levers.** That contrast is the single best thing in this inventory for a blog.

4. **The per-bit price list is an upper bound, high by about 2×, and the reason is now a law.** Summing the 32
   measured per-position prices over a random operand's own flip histogram over-predicts its measured step by
   2.3× (A side) and 2.0× (B side). It is **shared wires, not interaction**: eight mantissa bits *spread* cost
   +3.860 ± 0.052 W more than the *low* eight at the same Hamming weight (74 SE from the zero a "how many bits"
   law requires), and one saturating curve in the additive sum fits 15 B-side rungs to 0.232 W rms against
   1.358 W for the best possible law in Hamming weight alone and 6.062 W for pure additivity. Which bits flip
   beats how many. The A side's shape is **not** that law and is open.

5. **Three different zeros are in play and the published numbers mix them.** `over idle` (the claims-v3
   campaigns, the September strict runs, E64's model term), `over a running kernel on zero data` (E67's anchors,
   the E15 rail column) and `over a constant NON-zero operand` (every bit price). The middle and the last differ
   by the **8.6 W of lane un-gating** that zero operands buy; the first and the last differ by the whole zeros
   level. Every cell in `inventory.json` now carries a `basis` field, and `tables.md` marks it, because a table
   that mixes them silently would be wrong by 8.6 W of 24.66.

### The headline kinds table, one card, one clock

The full table is [`tables.md`](tables.md) §1A–1C. Its spine, on **aifoundry2 at a pinned 600 MHz**, over the
pre-launch idle, leakage-normalised (source: claims-v3 `abla.runs.json`, 4 passes per configuration):

| format | kind | switching W | pJ per MAC | physical-net toggles per MAC |
|---|---|---:|---:|---:|
| fp32 | zeros | 1.852 ± 0.090 | 0.403 | 0.004 |
| fp32 | ones | 10.367 ± 0.061 | 2.258 | 0.19 |
| fp32 | −0.0 (`m_negzero`) | 10.216 ± 0.027 | 2.225 | — |
| fp32 | signs | 15.415 ± 0.024 | 3.357 | 184 |
| fp32 | pow2 | 16.295 ± 0.012 | 3.549 | 288 |
| fp32 | a = randn, b = ones | 18.030 ± 0.058 | 3.927 | 571 |
| fp32 | a = ones, b = randn | 21.760 ± 0.095 | 4.739 | 436 |
| fp32 | truncated mantissa | 24.170 ± 0.067 | 5.264 | 1,014 |
| fp32 | randn | 27.181 ± 0.085 | 5.920 | 1,301 |
| fp16 | zeros | 1.881 ± 0.093 | 0.205 | — |
| fp16 | ones | 10.345 ± 0.034 | 1.126 | — |
| fp16 | randn | 24.435 ± 0.014 | 2.661 | — |
| int8 | zeros | 2.509 ± 0.017 | 0.0796 | — |
| int8 | ones | 4.387 ± 0.134 | 0.139 | — |
| int8 | randn | 9.885 ± 0.033 | 0.314 | — |

Two things in that table a blog reader will want pointed out. **fp32 ones and fp32 −0.0 are the same number**
(10.37 and 10.22 W, −0.15 W apart with a 95% interval of [−0.80, +0.50]): the chip gates the all-zero *bit
pattern*, and −0.0 is not that pattern, so a matrix of negative zeros costs what a matrix of ones costs.
And **int8 random is 19× cheaper per multiply-add than fp32 random** (0.314 against 5.92 pJ) while being only
6.9× faster, because int8 takes 318 cycles per op against fp32's 546.

### Speed, heat and the limit — the nine cells that exist

aifoundry2 under its own governor (TDP 65 W, threshold 65 °C), from [`tables.md`](tables.md) §1B:

| format | kind | burst MHz (cool die) | TFLOPS·TOPS burst | limit, burst | sustained MHz | TFLOPS·TOPS sustained | die °C sustained | limit, sustained |
|---|---|---:|---:|---|---:|---:|---:|---|
| fp32 | zeros | 792 ± 2 | 12.12 | none | 800 | 12.28 | 59.0 | none |
| fp32 | ones | 785 ± 11 | 11.98 | none | 738 | 11.12 | 65.4 | thermal |
| fp32 | randn | 703 ± 10 | 10.61 | power | 600 | 9.21 | 67.1 | thermal |
| fp16 | zeros | — | — | — | 794 | 24.37 | 59.0 | none |
| fp16 | ones | — | — | — | 737 | 22.25 | 65.4 | thermal |
| fp16 | randn | — | — | — | 601 | 18.43 | 66.1 | thermal |
| int8 | zeros | — | — | — | 800 | 84.32 | 59.0 | none |
| int8 | ones | — | — | — | 800 | 84.33 | 61.7 | none |
| int8 | randn | — | — | — | 763 | 79.48 | 65.3 | thermal |

The `limit` column is derived in `build_inventory.py` from each run's own governor events and its last-40 s
clock and die bins, by a stated rule, not read off a prose table. **int8 zeros and int8 ones both hold 800 MHz
for 80 s**: in int8, predictable data does not buy speed on this cooling, because random int8 is already only
9.9 W of switching and the die reaches only 65.3 °C. The Horace effect in int8 is 6%, in fp32 33%.

### The bit level

[`tables.md`](tables.md) §2A is the full 32-position price list on both operand sides, and §2B the ladders,
the orders, the one-gate prices, the register-file bound and the memory path. The shape:

- **B side** (the operand that changes every micro-op, 4,096 designed flips per multiply-add, A = 1.0):
  **82.9 fJ at bit 6 to 1,007.8 fJ at bit 22**, a 12.2× span. Bits 0–9 are flat at about 109 fJ; from bit 10 the
  price climbs monotonically. Exponent bits average 174 fJ, the sign bit 123 fJ.
- **A side** (the Booth-recoded operand, held across both micro-ops of a pair, so **2,048** designed flips per
  multiply-add, B = 1.0): **152.5 fJ at bit 4 to 1,440.4 fJ at bit 22**, a 9.4× span; exponent 265 fJ, sign 247 fJ.
  Median A/B ratio 1.60 over the 23 mantissa positions, and the A-side low mantissa is noticeably noisier
  (Spearman ρ 0.851 against the B side's 0.927) — bit 1 reads 503 fJ against bit 2's 209.
- **The busy partner** costs more at every shared position: A = π over A = 1.0 is 1.59–4.73×. On the ladder
  *slope*, though, it is only +11% (116.7 → 129.9 fJ): a single flip above a constant operand and a marginal
  flip in a stream of flips are different measurements.
- **Turning the data on costs more than the next bit does.** The first flip is 1.11× the ladder's own per-h slope
  with a quiet partner and **3.28×** with a busy one. A per-bit price is a local slope, never a tariff.
- **Voltage, not clock.** The same card reads 79.18 ± 3.09 fJ at 600 MHz / 0.5179 V and 121.27 ± 0.61 fJ at
  800 MHz / 0.6174 V. The clock-scaling rival (n = 3.637) is excluded in every reduction at ≥ 3.4 SE; the
  exponent itself is bracketed 1.60–2.92, not pinned at 2.
- **A flipped bit that never enters the multiplier still costs.** `sm_sgn` is 0.548 ± 0.111 W with *exactly zero*
  toggles in every tree-only RTL module. Between about a third and two thirds of a 12-bit mantissa flip's
  in-unit cost is the multiplier (s_mul 0.50 ± 0.15 ᵗ); the rest is the operand bus, the read ports, the result
  path and the accumulator.
- **The register file's cells cannot be the explanation**: < 2.73 fJ per flipped cell bit at 95% on the board
  (point 0.855, interval contains zero), 1.643 fJ [0.704, 2.583] on the minion rail. Per multiply-add that is
  0.055 pJ at the point and at most 0.175 pJ — 1.4% of the Q128 remainder, at most 4.6%.
- **The memory path** has two designed counts: changed bits and carried ones. L1 **0.0492 pJ per changed bit**
  [0.0482, 0.0501] and nothing per carried one; DRAM **3.255 pJ per carried one** [2.97, 3.55] and a changed-bit
  arm that is non-monotone in every kept pass, so a bound. Bit-counting explains **98.3%** of L1's
  zeros-to-random chord and **36.6%** of DRAM's.

### The mechanisms, in one list

[`tables.md`](tables.md) §3 and `inventory.json` > `mechanisms`. Eight of them, each with its size and its
source: zero gating (and the −0.0 exception, and the vector unit's missing zero gate), order, shared wires
(saturation), position inside the word, the busy partner, voltage-not-clock, carried ones off chip, and the
governor that turns all of it into speed.

## How the units were normalised, and what that cost

`inventory.json` > `normalisation` is the authority; this is the short form.

| what | the rule here | why it matters |
|---|---|---|
| MAC against flop | 1 multiply-add = 2 flops; one 16×16×16 TensorFMA = 4,096 multiply-adds, so MAC/s = ops/s × 4,096 = TFLOPS × 10¹² / 2 | the September tables are in pJ per flop, the claims-v3 tables in pJ per MAC, and they differ by exactly 2× |
| cycles per op | fp32 546, fp16 546, int8 318, identical on three cards to 0.0002 cycle | int8 is **6.9×** fp32's MAC rate at one clock, not 4× |
| 600 against 800 MHz | **never scaled by the clock ratio.** E64's own model uses (V/0.517)²·f/600, i.e. s(700) = 1.408 and s(800) = 1.905 over s(600) = 1.0, and every cell that crosses a clock is marked `modelled` and says so | E72 ran one card at both and found the board price **10–15% below** a pure V² extrapolation, with the clock-scaling rival excluded everywhere |
| card against card | aifoundry3 switches 0.958–0.969 of aifoundry2 at the same die temperature; a2's 600 MHz per-bit price is 0.970 of a3's | about 3% on any cross-card quote; aifoundry1 card 1 idled at 50.15 W against a2's 36.34 and a3's 25.78 and borrows a2's leakage slope |
| the baseline | three zeros, named per cell in `basis`: over idle (leakage-normalised or raw), over a running zeros kernel, over a constant non-zero operand | the middle and the last differ by 8.6 W of lane un-gating in a 24.66 W step |
| the leakage slope | each card's own **measured idle** slope in its own band: a2 0.2936 (51–58 °C) and 0.3452 (58–62); a3 0.3200 (52–58) and **0.3803 ± 0.0036** (58–62) | a slope is not a card constant: it rises ~0.009 W/°C per °C on a2 and ~0.011 on a3. E68's registered 1.508 W/°C is 4–5× every measured idle slope and is a busy transient; its prices are published at both footings |
| launch temperature | recorded per cell, never corrected across | switching power's own drift with die temperature is +22.0 ± 36.1 mW/°C (E65 D1; +32.4 ± 39.6 at E71's slope) — consistent with zero and UNDECIDED, so about ±1% per 10 °C of unremoved uncertainty |
| the September `switching_W` | marked ˢ: it is `p_early − p_before`, **not** leakage-corrected, and reads about **8% high** on fp32 randn (29.5 W against the leakage-normalised 27.2 W) | the ˢ-marked kinds (sparse75, sparse50, checker, ternary, pi, uniform) are the only route to those kinds, so the mark, not an exclusion |
| toggles | `nets_hier`, never `nets` | the 21 Sep figure of 21,331 net toggles per random fp32 multiply-add reproduces only under the Verilator it was measured with and was never a count of wires; the figure to quote is about 1,301, 8–16× smaller |
| board against rail | the minion rail carries 4.774 pJ [4.549–4.951] of the board's 5.783 pJ per random fp32 multiply-add, ratio 0.825 [0.787–0.856] | 0.875 pJ of the 1.009 pJ gap is the regulators' delivery loss, a named account and not a bottom-up row |

## The holes the card lanes fill

`inventory.json` > `holes` has all ten with their evidence and their method. Ranked:

| # | lane | the hole | what it costs the blog |
|---|---|---|---|
| H1 | **E78** | fp16 and int8 have only zeros, ones, randn | 44+ cells; two of three formats are a three-point line |
| H2 | **E79** | no per-bit price list for fp16 or int8 at all | fp16's PRM pseudo-code has a 2-term update only when all four of a1, a2, b1, b2 are non-zero, so fp16 may have a zero-gating rule fp32 has not — untested |
| H3 | **E80** | sustained clock, speed, die °C and the limit exist for 9 of 16 (format, kind) pairs | the burst-against-sustained distinction is the post's spine |
| H4 | **E80** | the fp16 all-ones sustained cell: 775 MHz predicted against 738 measured, n = 1 | the governor model's one standing miss, and it is an all-*ones* cell |
| H5 | E78 rail arm / **E77 (out of scope)** | no pJ per op at the minion rail over IDLE for any kind, none at all for fp16 or int8 | a reader asking "what does the chip pay" gets the board, which includes the regulators |
| H6 | desk | no toggle count for any fp16 or int8 kind | the bridge from the card to the gate-level ledger is fp32-only |
| H7 | E70 follow-up | the A side's saturating form is rejected and nothing replaces it | a two-sided prediction has no footing |
| H8 | **E81 (reserved)** | the DRAM pattern question: a third image at matched counts and a longer period | 63.4% of DRAM's chord is unexplained, and DRAM dominates a real workload |
| H9 | E74 follow-up / E77 | the register file's read ports, read mux tree and clocking | the hub's #1 item: the transport row charges 0.654 pJ per MAC in the zeros stimulus where the whole board costs 0.27 |
| H10 | desk | no kind measured on two cards at one clock AND one temperature | ~3–5% card term on every cell, on top of its own interval |

**What this lane did NOT do.** It ran no card, started no experiment and made no new measurement. It also did
not re-reduce anything: where a campaign published a number at a leakage slope later shown to be wrong (E68 at
1.508 W/°C), this inventory carries the published value and names the better footing in `conditions` rather than
silently substituting. H10's fix — re-reducing every campaign onto one launch temperature with each card's own
measured idle slope — is desk work that is still owed.

## Files

| path | what |
|---|---|
| `README.md` | this: results first, the normalisation, the holes |
| `inventory.json` | the whole inventory: `normalisation`, `typed_numbers`, `row_coverage`, 1,166 `operand_kind_cells`, 239 `bit_level_cells`, 8 `mechanisms`, 10 `holes`. Every cell carries `format`, `kind`, `quantity`, `value`, `interval`, `unit`, `conditions`, `source` (path + key), `status` and `basis` |
| `tables.md` | the markdown this README quotes: §1A/1B the kinds table, §1C the coverage matrix, §2A/2B the bit level, §3 the mechanisms. Generated; do not hand-edit |
| `build_inventory.py` | reads the committed JSON and writes both. No third-party modules |

Rebuild (any machine with Python 3, from the repository's top directory):

```bash
python3 docs/reports/data/2026-10-31-q130-kinds-inventory/build_inventory.py \
    --out docs/reports/data/2026-10-31-q130-kinds-inventory
```

### Where the numbers come from

| source file | experiment | what this inventory takes |
|---|---|---|
| `2026-09-25-claims-v3/results/abla.runs.json` | E38 | 23 configurations × 3 cards, 600 MHz: `switching` W and `per_s`, so switching W and pJ per MAC for the fp32/fp16/int8 kinds and six structured matrices |
| `2026-09-25-claims-v3/results/ablb.runs.json` | E39 | the A-side sparsity ladder (`nnz_a` 0–256 of 256) and the TenB arms × 3 cards. **Note:** the task brief calls these "E38's sparsity levels"; the sparsity ladder is in fact E39's `ablb` block, and E38's `abla` block holds the operand kinds and the structured matrices. Both are the 25–26 Sep three-card campaign |
| `2026-09-21-horace-aifoundry2/horace3.json` | E9 | the 14 patterns on aifoundry2: board over idle, the fitted electrical term, pJ per flop, TFLOPS, die rise and slope, the late rails |
| `2026-09-22-horace-aifoundry3/horace3.json` | E20 | the same 8 of those patterns on aifoundry3 |
| `2026-09-21-horace-aifoundry2/ablation.json` | E15 | the 14 structured matrices measured: `dyn`, `pj_per_unit_dyn`, `rails_late.minion`, `rise` |
| `2026-09-21-horace-aifoundry2/structured_predictions_before.json` | E14 | the same matrices **predicted** from RTL flip counts, written to disk 36 s before the first of them launched |
| `2026-10-26-toggle-recount/recount.json` | Q126(b) | `nets_hier` and `ff_clocked` per operand kind — the authoritative toggle count |
| `2026-10-23-e64-horace-power-limit/figures.json` | E64 | per-run board W, burst clock, TFLOPS, the governor model's `fit.c`/`fit.s`, the sustained block, the cap table, the thermal line |
| `2026-10-20-bitflip-ladder/hl.json` | E60 | the ladder slopes on three cards (board and rail), the first flip, the four orders, the one-gate prices |
| `2026-10-26-e65-bit-prices-hart-ladder/hl.json` | E65 | the B side at all 32 positions, and the five busy-partner positions |
| `2026-10-27-e67-a-side-bit-prices/hl.json` | E67 | the A side at all 32 positions, the busy partner, the 4×4 interaction grid, and the card anchors with their rails |
| `2026-10-27-e68-stage-map/verdicts.json` | E68 | the nine stage-map items, 800 MHz |
| `2026-10-27-e70-saturation-ladder/scored.json` | E70 | the saturating law, the matched-h layout contrast, every rung's fJ, the A-side rejection, the carry-over |
| `2026-10-27-e72-600mhz/verdicts.json` | E72 | the same card at 600 and 800 MHz, board and rail |
| `2026-10-28-e74-register-file-cells/rf.json` | E74 | the register-file cell bound, board and rail |
| `2026-10-28-e75-memory-flip-ladder/mf.json` | E75 | the four memory levels, changed bits and carried ones |
| `2026-10-21-dtf/dtf.json` | E61 | the one-gate, carry, cell, index and zero-gate derived quantities on aifoundry3 |
| `2026-10-27-e71-idle-slope-aifoundry3/slopes.json` | E71 | the measured idle slope the normalisation section quotes |

## What it changes

**For the blog:** the table exists, it is sourced cell by cell, and its shape is now a fact rather than an
impression — fp32 is dense, fp16 and int8 are three points each, and the *speed* half of the table is nine
cells. The three normalisation traps a writer would otherwise fall into (MAC against flop, clock against
voltage, and which zero) are each written down with the size of the error they cause.

**For the hub:** nothing in the Levels table moves — no number here is new. The Status tab's "what's missing
now" list gains the shape of the gap at item 9 (**fp16 and int8**): it is not one missing experiment but 44+
table cells and two whole price lists, and H3/H4 say which nine speed cells exist and which seven fp32 kinds
have power without speed.

**For the card lanes of this workflow:** E78, E79 and E80 each have a named cell list to fill, and H5 states
plainly that the minion-rail column cannot be closed without E77, which is out of scope today.
