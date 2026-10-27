# V3-HA: E67 — the A side of the price list, the busy partner, and the interaction grid (Q128)

*Pre-registered Mon 26 Oct 2026 (week 44) on aifoundry3, before the first measured pass; any change after this
commit goes in the Amendments section at the end, dated, before the data it touches. Request Q128(a). Card:
**aifoundry3 only**, whose governor is latched at 600 MHz by `et-board-clock-guard`
(`docs/findings/14-card-behaviour.md`) — the same card, clock and voltage as E65's B-side scan, so the two sides
add up on one footing. Every number below is a 600 MHz, ~0.523 V number.*

## Why

E65 (Q126, `tools/claims-v3/hb/README.md`) priced **one operand side**: all 32 positions of **B** with the quiet
partner A = 1.0, from 83 fJ at bit 6 to 1,008 fJ at bit 22, and the flow-M case (B bit 11 against A = π) at
745 ± 56 fJ per flipped bit at the board. **The A side has never been priced.** That leaves three holes in the
chain from "zeros run 15–33% faster than random fp32" down to a transistor:

1. **Half the operand bits have no price.** A random multiply-add flips bits on both operands. A per-bit model
   built on B alone has to assume A costs the same, and nothing has tested that. A is the **Booth-recoded**
   operand: it is broadcast to all eight lanes and drives the recoder that *selects* each partial product, while
   B is per-lane and *feeds* the partial-product muxes. Those are different paths, and they can have different
   prices per flipped bit.
2. **Two flips at once have never been measured.** Every price so far is a one-knob price. If a real workload's
   flips are sub-additive — the second flip finds the multiplier tree already switching — then summing per-bit
   prices over a Hamming distance over-counts, and by how much is unknown.
3. **The closure has no footing.** To test "summed per-bit prices reproduce the random-data step", the summands
   and the step must come from one card, one clock, one voltage and one pass set. They do not yet.

This experiment runs all three on the card E65 ran on, with E65's own protocol, so the two price lists are
directly addable.

## The A side flips every second cycle, and the count is 2,048, not 4,096

The issue order (PRM 9.4, `rtl-sim/fma_toggle`, `make_hl.py:issue_streams`) is: for each B row k, for each A row
i, two micro-ops (C columns 0–7 then 8–15). **A[i][k] is held across both**, and B alternates every micro-op. So
an A word can change only every *second* cycle: 16 transitions per B row × 16 B rows × 8 lanes = **2,048 designed
A-bit flips per multiply-add per minion**, exactly half of B's 4,096. This is a fact of the hardware's issue
order, not a choice, and it is why the A-side items must be divided by their own designed count. Every count is
re-derived from the written operand files by `make_hl.py --check`, and the reduction divides by the manifest's
own number, never by a constant.

## Departures from the ask, and why

- **D1, one shared A base word.** E60 and E65's `bit_<j>` draw a fresh random base per position, so an item minus
  its zero carries both the flip and the difference between two random words. Here **every A-side item shares one
  base word**, and the zero `aq_h0` is that same word held constant, so an item minus its zero differs in bit j
  alone. Bit 30 is the exponent MSB and cannot flip from exponent 127 (that is Inf), so it uses the
  exponent-64 twin of the same mantissa and gets **its own zero**, `aq_e64`. This is a tightening of E65's
  design, not a departure from it, and it is why the reduction needed a per-item zero (A12).
- **D2, no RTL predictions for the new items.** `predict_hl.py` needs Verilator, which is not on this host (E65's
  D3). Blocks 1–3 are registered against *measured* E65 anchors, not against an RTL replay; `reduce_hl.py` reports
  `pred_dW: null` for an item with no prediction.
- **D3, the grid is 4 × 4 on mantissa bits.** Positions {0, 8, 16, 22}: all mantissa, so one base word serves
  every cell and no cell needs a different exponent. 25 items on one base — the 16 cells, the 4 A-only and 4
  B-only margins, and the base itself — so the interaction is a within-pass, within-base contrast.
- **D4, launch reading unchanged.** E65 launched every run on this card at 58 °C after 59 °C and the card still
  idles at about 52 °C. The same pair is used, so E65's and E67's runs are launched identically.

## Block 1 — the 32-position A scan (the A side of the price list)

`abit_<j>`, j = 0..31: A's bit j alternates down the rows, **B = 1.0 everywhere** (the quiet partner, exactly
E65's block A with the operands swapped). 2,048 designed A-bit flips per multiply-add. Zero: `aq_h0`
(`aq_e64` for j = 30).

## Block 2 — the busy partner (the A-side mirror of the flow-M case)

`abp_<j>`, j ∈ {0, 8, 11, 16, 22}: the same single-bit alternation of A with **B = π**. Zero: `ap_h0` (A constant,
B = π). `abit_<j>` and `abp_<j>` share their A words, so the pair isolates what the partner costs at one position.
`abp_11` is the mirror of E65's `bpi_11`, the stimulus Q124 priced at the gate level from the design files.

## Block 3 — the interaction grid (how two flips at once add)

`ix_<i>_<j>` for i, j ∈ {0, 8, 16, 22}: A's bit i and B's bit j alternating **together**, on one constant base.
Margins `ix_a<i>` (A alone), `ix_b<j>` (B alone) and the base `ix_z`, all on the same words. The quantity is the
paired contrast per pass

    excess(i, j) = [cell − A-only] − [B-only − base] = cell − A-only − B-only + base,

which cancels the base and every pass-level offset. Zero excess = the two flips cost the sum of each alone.

## Block 4 — the anchors, on the same card and pass set

`anchor_zeros`, `anchor_ones`, `anchor_pi`, `anchor_randn` (the built-in `--values` patterns of 21 Sep), plus two
one-sided random items: **`nrd_a`** (A random fp32, B = 1.0; 27,648 designed A bits per multiply-add) and
**`nrd_b`** (A = 1.0, B random fp32; 56,784 designed B bits). Ties to E65: `lq_h0` and `lb_h0` run in every
block-1 pass. These are the anchors the closure job reads summed per-bit prices against.

## Protocol, shared

Blocks 1, 2 and 4 run as one pass list; block 3 as its own. Both go through `hl/block.sh` (E60's, unchanged),
which holds `flock -n /run/lock/etsoc-shire0.lock` for the pass, puts every device process under `timeout 10`
with `--stop-file`, stops at a 78 °C reading or on telemetry older than 3 s, writes `et-lab-manifest` and
`gen.sha256` beside the data, and releases the lock between passes. E60's departure D1 (another user's idle login
does not block; another user *on this card* does, failing closed) stands. Before the first launch:
`et-boot-check --status`, `et-who`, `who`, `uptime`, and a `V3_DRY=1` dry run of both lists. The card is claimed
in `#community-lab` before the first launch and released after. If anyone else takes the card, stop and wait.
Card time at most 2.5 h in total. Operand set `build/hl-gen4`; every file E60 and E65 ran is byte-identical in it
(87 of 87, checked before the first launch).

## Pre-registered analysis

`hl/reduce_hl.py`, amended as A12 below. Per run, P = mean board power over [t₀+1 s, t₀+3 s) corrected to the
launch reading with the card's leakage slope; gates on one clock, voltage within 3 mV of the pass median, an
on-protocol launch within 0.5 °C of the target, and fma cycles per op within 0.5% of the item's **own zero** in the
pass. Every item minus its own zero per pass; the unit of replication is the pass; SE from the between-pass
scatter. A pass with more than one failed run, or an `anchor_pi` drift above 0.3 W from first to last, is set
aside. Per-position price = (item − zero) / (designed bits per op × ops per second), in J per alternating bit,
with C = 2E/V² and electrons Q = CV/e beside it.

## Predictions, frozen with this commit

- **P1 (the A scan rises with the bit).** Over the mantissa field (j = 0..22) with B = 1.0 the A-side price rises
  with j: Spearman ρ > 0.5 over the 23 positions, and the span over all 32 positions exceeds 5×. *(E65's B side:
  83 fJ at bit 6 to 1,008 fJ at bit 22, a 12× span.)*
- **P2 (the two sides are within a factor of 3, and correlated).** At each of the 23 mantissa positions the
  A-side price is within a factor of 3 of E65's B-side price at the same position, and the two are positively
  correlated across those positions (Spearman ρ > 0.5). Both operands enter the same multiplier array, so a large
  common component is expected; the Booth recoder makes A's path shallower in logic but wider in fan-out, so an
  offset is expected too. **A ratio outside [1/3, 3] at most positions is the headline result**, and means a
  one-number-per-flipped-bit model cannot serve both sides.
- **P3 (the cheap end).** The sign bit (31) is among the four cheapest A positions, and the exponent bits (23–30)
  cost more than the mantissa bits below 16.
- **P4 (the busy partner costs more).** At every shared position `abp_<j>` − `abit_<j>` > 0, and at ≥ 2 SE for at
  least 3 of the 5 positions (E60's ladders: 129.9 fJ with a busy partner against 116.7 fJ with a quiet one, +11%).
- **P5 (the flow-M mirror).** `abp_11` lands within a factor of 3 of E65's `bpi_11`, 745 ± 56 fJ per flipped bit
  at the board. Outside that band the two operand paths are genuinely asymmetric at the position the chip diagram
  priced, and the gate-level price (0.11–0.13 pJ, 381 physical wires, `tfma.flip.gate`) is a B-side price only.
- **P6 (two flips add).** Every cell's excess over the sum of its margins is within ±0.5 W of zero, the mean
  excess is within ±0.3 W, and |excess| is under 20% of that cell's sum for at least 12 of the 16 cells.
- **P7 (the one-sided anchors).** d(`nrd_a`) / d(`nrd_b`) ∈ [0.3, 0.8] — A flips 27,648 designed bits against B's
  56,784, a ratio of 0.49, so a price-per-bit that is equal on the two sides predicts about 0.49.
- **P8 (the closure, reported with its interval).** Summing the measured per-position prices over `nrd_a`'s and
  `nrd_b`'s designed bit counts predicts their measured steps within a factor of 2. This is the first test of
  whether the per-bit price list reproduces a random-data step on its own card; it is scored, and the ratio is
  reported whatever it is.

## Decision rules

Each prediction is scored PASS / FAIL / UNDECIDED against its own stated band, in the results section of the data
README and in E67 of `docs/findings/03-experiments.md`. UNDECIDED is used when the measurement's SE cannot
separate the bands. A block whose passes do not survive the gates is reported as not run, never re-registered.
P6's three parts are scored together: all three hold = additive; mean excess below −0.5 W at > 3 SE =
sub-additive, above +0.5 W at > 3 SE = super-additive; anything else = undecided with its interval.

## Files

`run_e67.sh` (the driver on the box). Blocks 1–4 use `tools/claims-v3/hl/` with amendments A11 and A12, whose
generator writes `build/hl-gen4`.

## Amendments

**A11 to `tools/claims-v3/hl/make_hl.py` (Mon 26 Oct 2026, with this commit, before any E67 data).**
- New helpers `a_base_words`, `a_tiles` and `randn_words`, and seven new families: `aq` (`aq_h0`, `aq_e64`),
  `ap` (`ap_h0`), `abit_<j>` for all 32 positions, `abp_<j>` for j ∈ {0, 8, 11, 16, 22}, `ix` (25 items), and
  `nrd` (`nrd_a`, `nrd_b`). Items carry a per-item `zero` field where the family map cannot name one.
  *Why:* the three holes above. **Every file E60 and E65 ran is byte-identical in `build/hl-gen4`** (87 of 87,
  checked on the box before the first launch), so nothing already measured changes.

**A12 to `tools/claims-v3/hl/reduce_hl.py` (Mon 26 Oct 2026, with this commit, before any E67 data).**
- `item_zero()`: an item's `zero` field from the manifest wins over the family map, both in the cycles-per-op gate
  and in the item differences. Every E60 and E65 item has no such field and keeps the family map, so their
  reductions are unchanged. *Why:* bit 30's base is the exponent-64 one and needs its own zero, and `nrd_a` /
  `nrd_b` sit on opposite sides.
- New reported sections `a_bits`, `a_bits_pi`, `a_partner`, `ix` and `anchors`. The A-side per-bit price divides
  by the item's **own** designed count from the manifest (2,048), not by the B side's 4,096.
