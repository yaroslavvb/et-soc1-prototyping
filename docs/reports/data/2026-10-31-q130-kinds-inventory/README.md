# Q130(a) — the kinds-of-numbers inventory, from what is already measured

*Sat 31 Oct 2026 (week 44), desk lane of Q130, on the Intel. **No card was touched.** Every number here is
read out of a committed file by [`build_inventory.py`](build_inventory.py); the few that have no
machine-readable form are typed into that script's `TYPED` dict with a citation and are marked ᵗ wherever
they appear (how many: `inventory.json` > `meta.cell_counts.typed_numbers`, five as this is written — the
zeros→random split used to be a sixth and is now computed). Built for the follow-up blog post to Horace He's
result — the table the post will quote, and the list of holes the card lanes of this workflow fill.
**Corrected the same day** after adversarial verification of the first cut (commit `7d9b73c5`); every
correction is listed in [§What the verification changed](#what-the-verification-changed).*

## Results

**One set of denominators, computed in `inventory.json` > `row_taxonomy`, and nothing may quote one of them
against another:**

> **52** (format, kind) rows have at least one run-sourced cell (fp32 43, fp16 4, int8 5); **3** more fp32
> matrices are prediction-only, so the cell list holds **55** rows. Folding the **10** configuration variants
> (the same operand stream at another minion count, or with TenB streaming) into their base kind leaves
> **42 distinct kinds of number** with a measured cell: **fp32 36, fp16 3, int8 3.**

1,166 operand-kind cells and 239 bit-level cells are already measured, modelled or predicted; the whole thing
is in [`inventory.json`](inventory.json) and laid out in [`tables.md`](tables.md).

**Five findings a reader of the inventory should take away before the blog is written.**

1. **The kinds ladder is fp32's alone.** fp32 has **36 measured kinds of number**; fp16 and int8 have **three
   each** — zeros, ones, random normal (plus a TenB streaming arm, which is a configuration of randn or ones,
   not a fourth kind). Both of the formats a reader would actually run inference in are a three-point line.
   That is E78's and E79's whole reason to exist. The figure to quote is 36 / 3 / 3, never 46: three of fp32's
   46 cell-list rows are prediction-only and seven are the same randn operand at another minion count.

2. **Power is measured almost everywhere; SPEED is measured almost nowhere.** `switching_W` exists for 53 rows
   and is **measured on 48** (the other five are three prediction-only matrices and two minion-count rows
   modelled from E64's fit); `pJ_per_MAC` exists for 50 and is measured on 48. `sustained_MHz`,
   `die_C_sustained` and `limit_sustained` exist for **nine** —
   E64's SUS block, three kinds × three formats. Seven fp32 ladder kinds have a cool-die burst clock and no
   sustained cell at all. The blog's headline distinction (burst = the power test, sustained = the thermal test)
   is the part of the table with the fewest cells in it.

3. **The two ends of the chain disagree about what "data-dependent" means.** In the multiply-add, what costs is
   **transitions**: the same 4,096 multiply-adds presented in max-flip rather than Gray order cost
   +0.682 ± 0.010 W more at **600 MHz / 0.522 V** (aifoundry3) and +1.291 ± 0.009 W at **800 MHz / 0.617 V**
   (aifoundry2), for identical results. That 1.9× is the **operating point, not the card**: 0.6825 × E64's
   *s*(800) = 1.90517 gives 1.300 W against aifoundry2's measured 1.291 W. On the DRAM
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
   by the **8.55 ± 0.06 W of lane un-gating** that zero operands buy; the first and the last differ by the whole
   zeros level. Every cell in `inventory.json` now carries a `basis` field, and `tables.md` marks it, because a
   table that mixes them silently would be wrong by 8.55 W of 24.66 ± 0.37.

   That split is now **computed**, not typed, in `inventory.json` > `zeros_random_split`: E67's `anchor_zeros`
   27.828 ± 0.043 W and `anchor_randn` 52.487 ± 0.364 W against E70's constant-operand level 36.383 ± 0.042 W
   (the mean of `lq_h0` 36.466, `aq_h0` 36.328 and `anchor_pi` 36.354, whose 0.138 W spread is the real
   uncertainty). E70's README rounds it to 8.6 / 16.1 / 24.66 W. All three levels are `p80` — board power with
   each run's own leakage rise since its **58 °C launch** removed — so no leakage term survives the difference:
   re-reducing both campaigns from their raw runs at one common slope moves the un-gating term by 0.105 W
   between E70's registered 0.1975 W/°C and E71's steepest measured 0.3803 W/°C, against its own 0.060 W
   standard error. (The two reducers used 0.1755 W/°C (E67) and 0.1975 (E70), solved from their own runs.)

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

Two things in that table a blog reader will want pointed out. **fp32 ones and fp32 −0.0 are the same number
on this card** (10.37 and 10.22 W, −0.151 W apart, 95% [−0.33, +0.03]): the chip gates the all-zero *bit
pattern*, and −0.0 is not that pattern, so a matrix of negative zeros costs what a matrix of ones costs.
State that carefully, because the registered item behind it is **not** a clean pass
(`inventory.json` > `registered_items.ABL-T1`):

- the intervals **as published** in `abla.json` are Bonferroni family-wise at α = 0.01/19 = **0.000526**, not
  95%: aifoundry2's is [−0.80, +0.50], about 3.6× wider than the 95% interval above, which is re-read here from
  the item's own point, se and df;
- ABL-T1's registered outcome is **CARD-DIFFERENT**: the ±1 W equivalence subtest passes on aifoundry2 and
  **FAILS on aifoundry3** (−0.039 W, published [−1.14, +1.06]) and **aifoundry1 card 1** (−0.144 W, published
  [−1.44, +1.15]) — on interval **width**, not on sign. Every point estimate is within 0.15 W of zero and all
  three 95% intervals lie inside ±1 W, so the mechanism reading holds while the registered equivalence does
  not. The other subtest (−0.0 is **not** gated like +0.0, > +6 W) passes on all three cards.

And **int8 random is 19× cheaper per multiply-add than fp32 random** (0.314 against 5.92 pJ) while being only
6.9× faster — 318 cycles per op against fp32's 546, *and* 16,384 MACs per TensorFMA against fp32's 4,096
(546/318 × 4 = 6.87).

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
for 80 s**: in int8, predictable data does not buy speed on this cooling, because random int8 draws only
**≈17 W of switching at the governor's own 800 MHz footing** — `fit.c[SUS-08…]` 9.101 W × *s*(800) 1.90517 =
17.34 W, the figure the table above carries — against random fp32's 49.27 W (25.862 × 1.905), so its die
reaches only 65.3 °C and it still holds 763 MHz. (int8 randn's **9.885 W** is a *pinned 600 MHz* measurement
from claims-v3; quoting it to explain an 800 MHz governor run crosses exactly the clock this lane set out to
keep straight.) Read the gap with its direction stated: sustained fp32 zeros are **33.3% faster** than fp32
randn (equivalently, randn is 25.0% slower); in int8, ones are **6.1% faster** than randn (randn 5.7% slower).

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
| MAC against flop | 1 multiply-add = 2 flops, so **in every format** MAC/s = TFLOPS·TOPS × 10¹² / 2. MACs per 16×16×16 TensorFMA are **format-dependent**: **fp32 4,096 / fp16 8,192 / int8 16,384** (`tools/claims-v3/hpl/surface_hpl.py:32` gives flops per op 8192 / 16384 / 32768) | the September tables are in pJ per flop, the claims-v3 tables in pJ per MAC, and they differ by exactly 2×. **`MAC/s = ops/s × 4,096` is fp32 only**: applied to fp16 it reports pJ per MAC 2× too high, to int8 4× too high. claims-v3's `per_s` is already MAC/s (`unit: MAC`) — 4.591e12 fp32, 9.184e12 fp16, 3.153e13 int8 at one 600 MHz pin |
| cycles per op | fp32 546, fp16 546, int8 318, identical on three cards to 0.0002 cycle | int8 is **6.9×** fp32's MAC rate at one clock (546/318 × 16,384/4,096 = 6.87) — not 1.7× from the cycles alone, not 4× from the MACs per op alone |
| 600 against 800 MHz | **never scaled by the clock ratio.** E64's own model uses (V/0.517)²·f/600, i.e. s(700) = 1.408 and s(800) = 1.905 over s(600) = 1.0, and every cell that crosses a clock is marked `modelled` and says so | E72 ran one card at both and found the board price **10–15% below** a pure V² extrapolation, with the clock-scaling rival excluded everywhere |
| card against card | aifoundry3 switches 0.958–0.969 of aifoundry2 at the same die temperature; a2's 600 MHz per-bit price is 0.970 of a3's | about 3% on any cross-card quote; aifoundry1 card 1 idled at 50.15 W against a2's 36.34 and a3's 25.78 and borrows a2's leakage slope |
| the baseline | three zeros, named per cell in `basis`: over idle (leakage-normalised or raw), over a running zeros kernel, over a constant non-zero operand | the middle and the last differ by 8.55 ± 0.06 W of lane un-gating in a 24.66 ± 0.37 W step (`zeros_random_split`) |
| the leakage slope | each card's own **measured idle** slope in its own band: a2 0.2936 (51–58 °C) and 0.3452 ± 0.0056 (58–62); a3 0.3200 ± 0.0038 (**51–58**, E71's own band label — its floor is 52–53 °C, so that fit spans 5–6 degrees) and **0.3803 ± 0.0036** (58–62). **Scope:** this rule reaches the a3 bit ladders, which launch at 58 °C inside the measured bands, and E71's `leak_sensitivity.py` re-prices exactly those | a slope is not a card constant: it rises ~0.009 W/°C per °C on a2 and ~0.011 on a3. E68's registered 1.508 W/°C is 4–5× every measured idle slope and is a busy transient; its prices are published at both footings. **It does NOT reach table 1A's spine:** every claims-v3 / September cell there is priced at an 80.9 °C (a2) or 55.8 °C (a3) launch on the campaign's own *fitted busy-die* slope, 0.81 / 0.55 W/°C — 2.1–2.8× every measured idle slope, at a die temperature no measured band covers (they stop at 66 °C). Re-reducing that campaign onto a measured slope is hole **H10** and is still owed |
| launch temperature | recorded per cell, never corrected across | switching power's own drift with die temperature is +22.0 ± 36.1 mW/°C (E65 D1; +32.4 ± 39.6 at E71's slope) — consistent with zero and UNDECIDED, so about ±1% per 10 °C of unremoved uncertainty |
| the September `switching_W` | marked ˢ: it is `p_early − p_before`, **not** leakage-corrected. Quote the offset **per quantity**, because it is not one number: on fp32 randn `switching_W` reads **+8.6% high** (29.52 against the leakage-normalised 27.18 W) and **pJ per MAC +12.0%** (6.630 against 5.920). The extra 3.1% is the denominator — the September pJ column implies 8.905 TFLOPS where the same record's `tflops` field reads 9.183 | the ˢ-marked kinds (sparse75, sparse50, checker, ternary, pi, uniform) are the only route to those kinds, so the mark, not an exclusion. §1A puts September sparse75 (1.0966 pJ/MAC ˢ) in the same pJ column as the claims-v3 figures: a reader comparing across that mark is comparing bases a tenth apart, not 8% |
| toggles | `nets_hier`, never `nets` | the 21 Sep figure of 21,331 net toggles per random fp32 multiply-add reproduces only under the Verilator it was measured with and was never a count of wires; the figure to quote is about 1,301, 8–16× smaller |
| board against rail | the minion rail carries 4.774 pJ [4.549–4.951] of the board's 5.783 pJ per random fp32 multiply-add, ratio 0.825 [0.787–0.856] | 0.875 pJ of the 1.009 pJ gap is the regulators' delivery loss, a named account and not a bottom-up row |

## The holes the card lanes fill

`inventory.json` > `holes` has all ten with their evidence and their method. Ranked:

| # | lane | the hole | what it costs the blog |
|---|---|---|---|
| H1 | **E78** | fp16 and int8 have only zeros, ones, randn (3 kinds each against fp32's 36) | 44+ cells; two of three formats are a three-point line |
| H2 | **E79** | no per-bit price list for fp16 or int8 at all | fp16's PRM pseudo-code has a 2-term update only when all four of a1, a2, b1, b2 are non-zero, so fp16 may have a zero-gating rule fp32 has not — untested |
| H3 | **E80** | sustained clock, speed, die °C and the limit exist for 9 of 16 (format, kind) pairs | the burst-against-sustained distinction is the post's spine |
| H4 | **E80** | the fp16 all-ones sustained cell: measured **737.1** MHz against Q129's own fp16 band **744.9–758.4** MHz, a +7.8…+21.3 MHz miss that no (γ, trip) pairing closes; n = 1 | the one sustained cell every candidate governor surface misses, and it is an all-*ones* cell. **E80 registers 744.9–758.4 MHz for it.** The 775 MHz figure is the **fp32** all-ones cell (`chain.py`, measured 737.9), whose miss Q129 narrows to +18.5…−7.8 MHz; the two cells both measure ~738 MHz, which is how they got welded together |
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
| `inventory.json` | the whole inventory: `normalisation`, `row_taxonomy` (the one set of row and kind denominators), `zeros_random_split` (computed, with its interval and footing), `registered_items` (ABL-T1 at its own α, with its two FAILs), `typed_numbers`, `row_coverage`, 1,166 `operand_kind_cells`, 239 `bit_level_cells`, 8 `mechanisms`, 10 `holes`. Every cell carries `format`, `kind`, `quantity`, `value`, `interval`, `unit`, `conditions`, `source` (path + key), `status` and `basis`, and a configuration variant also carries `variant_of` and `variant_is` |
| `tables.md` | the markdown this README quotes: §1A/1B the kinds table, §1C the coverage matrix over **every one of the 55 rows** (variants marked ᵛ), §2A/2B the bit level, §3 the mechanisms. Generated; do not hand-edit |
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
| `2026-09-21-horace-aifoundry2/structured_predictions_before.json` | E14 | the same matrices **predicted** from RTL flip counts, written to disk at `made_at` **2026-09-21T13:08:33**, "before any of these matrices had run on the card" (the file's own `note`). The measured figures they are scored against are the claims-v3 `abla` runs of **26 Sep** (earliest aifoundry2 run `t0` 1790391404.347 = 2026-09-26T02:56:44 UTC). No shorter lead time is checkable from this repository: the same-afternoon session's `t0` values in `validation_afternoon.json` are relative offsets into session `long2` with no absolute anchor committed, so the "36 s before the first launch" of the first cut is **withdrawn** |
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

## What the verification changed

Adversarial verification of the first cut (commit `7d9b73c5`) returned **holds-with-fixes**: every cell value
it re-derived reproduced exactly, including the SEMs and the stated derivation rules, and the public-text scan
was clean. What did not hold was the counting layer and a handful of blog-facing sentences. All of it is
corrected here, on the same day, with no card touched and no experiment re-run:

| # | what was wrong | what it now says |
|---|---|---|
| 1 | "52 (format, kind) rows" and "fp32 has 46 kinds" were two denominators quoted as one (46+4+5 = 55, not 52) | one computed set in `row_taxonomy`, quoted verbatim in the Results and in `tables.md` §1 |
| 2 | "fp32 has 46 **measured** kinds" counted 3 prediction-only matrices and 7 minion-count variants of randn | **36** fp32 / 3 fp16 / 3 int8 distinct kinds of number, folded by `VARIANT_OF`; each variant cell carries `variant_of` |
| 3 | "power is measured for 53 rows" | `switching_W` exists for 53 rows, **measured on 48** |
| 4 | the handoff normalisation said "MAC/s = ops/s × 4,096" for every format — 2× wrong for fp16, 4× for int8 | MACs per TensorFMA **4,096 / 8,192 / 16,384**, and MAC/s = TFLOPS·TOPS × 10¹² / 2 in every format |
| 5 | ABL-T1's interval was called "95%" and only the card it passed on was reported | labelled at its own α = 0.000526, re-read at 95%, and the two FAILs (a3, a1c1) named, with the registered outcome **CARD-DIFFERENT** — `registered_items.ABL-T1` |
| 6 | "written to disk 36 s before the first of those matrices launched" had no committed source | **withdrawn**: predictions dated 2026-09-21T13:08:33, measurements 26 Sep, and a note that no shorter lead time is checkable from this repo |
| 7 | an 800 MHz governor result was explained with int8 randn's **9.9 W** pinned-600 MHz figure | ≈**17.3 W** at the governor's 800 MHz footing against fp32 randn's 49.3 W, with the 600 MHz figure named as such |
| 8 | H4 spliced the **fp32** cell's 775-vs-738 miss onto the **fp16** cell | E80's fp16 all-ones prediction registers at **744.9–758.4 MHz** (measured 737.1); 775 belongs to fp32 |
| 9 | "9.209 TFLOPS is 33% below zeros" | zeros are **33.3% faster**, randn **25.0% slower** — the direction is stated wherever the gap appears |
| 10 | "the five typed numbers" when there were six | the split is **computed** (so five remain) and the count is emitted as `meta.cell_counts.typed_numbers` |
| 11 | "a3 0.3200 over 52–58 °C" — no such band | **51–58 °C**, E71's own label, with its 52–53 °C floor noted |
| 12 | the measured-slope rule flagged E68's 1.508 W/°C but left table 1A's own 0.81 W/°C unflagged | the rule's **scope** is stated: it governs the a3 ladders, not the 80.9 °C claims-v3 cells, whose re-reduction is H10 |
| 13 | §1C, "a coverage matrix", held 36 of the rows with no note | **all 55 rows**, variants marked ᵛ, with a line for the two that carry only an over-constant cell |
| 14 | the 8.6 / 24.66 W split was typed, with no interval and no footing | **computed**: 8.55 ± 0.06 / 16.11 ± 0.37 / 24.66 ± 0.37 W, all three levels `p80` at a 58 °C launch, with the slope sensitivity measured (0.105 W) |
| 15 | the September offset was given as "~8% high" for both columns | **+8.6% on `switching_W`, +12.0% on pJ per MAC**, with the 3.1% denominator difference named |
| 16 | the headline max-flip contrast read as card-against-card | it is an **operating point**: +0.68 W at 600 MHz / 0.52 V and +1.29 W at 800 MHz / 0.62 V; 0.6825 × *s*(800) = 1.300 W against a2's measured 1.291 |

One of the verifier's own statements does **not** survive checking, and the correction is made on the data
rather than on its wording: fault 14's evidence says E67's anchors are "leakage-corrected at E71's 0.3803 W/°C".
They are not — E67's own runs imply **k = 0.1755 W/°C** exactly, and E70's 0.1975, each constant to the last
digit over every aifoundry3 run with a non-zero window rise (solved from `p_raw`, `p80`, `t_win` and
`start_c`, which is 58.0 °C on all 554 E67 and 203 E70 runs). The two footings were therefore much closer
than the fault claims, which is why re-footing both on one slope moves the split by 0.105 W. The substance of
the fault stands and is fixed: the figure had no interval and did not say what it was referred to.

## What it changes

**For the blog:** the table exists, it is sourced cell by cell, and its shape is now a fact rather than an
impression — fp32 has 36 measured kinds, fp16 and int8 three each, and the *speed* half of the table is nine
cells. The three normalisation traps a writer would otherwise fall into (MAC against flop — **per format**,
clock against voltage, and which zero) are each written down with the size of the error they cause, and the
fourth, counting configurations as kinds, is now impossible to fall into: `row_taxonomy` computes one answer.

**For the hub:** nothing in the Levels table moves — no number here is new. The Status tab's "what's missing
now" list gains the shape of the gap at item 9 (**fp16 and int8**): it is not one missing experiment but 44+
table cells and two whole price lists, and H3/H4 say which nine speed cells exist and which seven fp32 kinds
have power without speed.

**For the card lanes of this workflow:** E78, E79 and E80 each have a named cell list to fill, and H5 states
plainly that the minion-rail column cannot be closed without E77, which is out of scope today.
