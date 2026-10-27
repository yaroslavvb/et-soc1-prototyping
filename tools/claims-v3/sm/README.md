# V3-SM: E68 — the stage map, which pipeline stage spends a flipped bit's energy (Q128)

*Pre-registered Mon 26 Oct 2026 (week 44) on aifoundry2, before the first measured pass; any change after this
commit goes in the Amendments section at the end, dated, before the data it touches. Request Q128(b). Card:
**aifoundry2 only**, whose governor is active and starts at 800 MHz — every number below is an 800 MHz,
~0.604 V number, and every item is sized to stay well under the governor's ~65 W power limit (Power, below).*

## The gap this closes

The chain from "zeros multiply faster than random data" down to one transistor switching has a hole at step 5→6.
E60 and E65 priced **a flipped operand bit** at the board — 116.7 / 129.9 fJ for the two ladders, 83 fJ to
1,008 fJ across the 32 B-side positions, 745 ± 56 fJ for the flow-M case. Q126(d) and Q126(e) priced the same
flips at the **gate level**, per stage. Nothing on a card has ever said **where in the pipeline the measured
energy goes** — so the gate-level stage split has never been tested against the hardware, and a model that
turns a Hamming distance into watts has no way to know whether it is pricing the multiplier or the adder.

E68 measures that split, using a contrast that is exact in the arithmetic rather than approximate in a model.

## The lever: an fp32 multiplier never sees a sign or an exponent

The TensorFMA32's multiplier (tfma.booth.rows) Booth-recodes **a's significand** and sums rows that are 0, ±b,
±2b in **b's significand**. The operand signs meet in one XOR and the exponents in one small adder, both outside
the tree. So:

- an item whose two alternating B words **share their significand** and differ only in the sign bit or the
  exponent field drives **bit-identical switching** through the Booth rows, the Wallace tree, its register and
  the product adder — **f1 and f2 are frozen by construction** — while f3 (align), f4 (add + leading-one),
  f5 (normalise) and f6 (round) see two different results every cycle;
- an item whose two B words **share sign and exponent** and differ only in low significand bits moves f1 and f2
  and leaves the product's exponent, and so f3's shift distance, where it was.

Eleven items, one shared base, each differing from its family's zero in **its mask alone** (asserted from the
files by `make_sm.py --check`, which also asserts `frozen_significand` for the four frozen items).

| item | mask | A | designed B bits / op | what it moves |
|---|---|---|---:|---|
| `smz_q` | — | 1.0 | 0 | the quiet family's zero |
| `smz_b` | — | π | 0 | the busy family's zero |
| `sm_lo12` | `0x00000fff` | 1.0 | 49,152 | f1/f2 only, mantissa bits 0–11 |
| `sm_hi12` | `0x007ff800` | 1.0 | 49,152 | f1/f2 only, mantissa bits 11–22 |
| `sm_sp12` | `0x002ab555` | 1.0 | 49,152 | f1/f2 only, 12 bits spread over 0–22 |
| `sm_sgn` | `0x80000000` | 1.0 | 4,096 | **f1/f2 frozen**; the add becomes a subtract |
| `sm_e1` | `0x00800000` | 1.0 | 4,096 | **f1/f2 frozen**; f3 shift distance 1 |
| `sm_e16` | `0x08000000` | 1.0 | 4,096 | **f1/f2 frozen**; f3 shift distance 16 |
| `sm_e64` | `0x20000000` | 1.0 | 4,096 | **f1/f2 frozen**; f3 saturates, the add is trivial |
| `sm_sgnlo` | `0x80000fff` | 1.0 | 53,248 | both: the additivity test |
| `sm_pi_sgn` | `0x80000000` | π | 4,096 | **f1/f2 frozen**, with a busy partner |

Plus `anchor_pi` (the drift anchor, run first and last in every pass by `run_hl.py`) and `anchor_zeros` (the
gated floor, context only).

## The RTL design matrix, frozen with this commit

`predict_sm.py` ran every item through the `rtl-sim/fma_toggle` bench on the Intel under **Verilator 5.052**
(not aifoundry2's 5.042, whose toggle coverage over-counts `txfma_csa` and `txfma_4_2_compressor` 7.9× and
9.0×: `rtl-sim/fma_toggle/README.md`), at accumulator points 1e3 and 4e5 ops, averaged, then differenced
against each item's own zero. Toggles are **RTL names**, per TensorFMA32 op (4,096 multiply-adds, one minion);
a physical net carries about 2.55 of them (tfma.names), and the wrapper files (`txfma_top`, `txfmactl_top`,
`txfmafrac_top`, `txfmaexp_top`) are mostly the datapath's own wires named again one level up, which is why
they are kept in their own column rather than spread over the stages.

MUL = the Booth rows, the Wallace tree, its compressors and the product adder (f1 + f2).
BACK = align + add/leading-one + normalise + round (f3 + f4 + f5 + f6).

| item | MUL | BACK | f0+ctl | all nets | MUL share of MUL+BACK |
|---|---:|---:|---:|---:|---:|
| `sm_lo12` | 4,199,936 | 2,091,264 | 1,754,315 | 8,045,515 | 0.668 |
| `sm_hi12` | 4,257,536 | 2,749,440 | 1,986,464 | 8,993,440 | 0.608 |
| `sm_sp12` | 5,159,424 | 3,146,240 | 2,227,617 | 10,533,281 | 0.621 |
| `sm_sgn` | **0** | 116,480 | 473,600 | 590,080 | 0.000 |
| `sm_e1` | 29,440 | 229,632 | 674,800 | 933,872 | 0.114 |
| `sm_e16` | 28,416 | 274,944 | 828,400 | 1,131,760 | 0.094 |
| `sm_e64` | 51,968 | 369,920 | 1,060,336 | 1,482,224 | 0.123 |
| `sm_sgnlo` | 4,199,936 | 2,207,744 | 2,227,915 | 8,635,595 | 0.655 |
| `sm_pi_sgn` | **0** | 122,112 | 474,112 | 596,224 | 0.000 |

Two facts the bench confirms rather than assumes:

1. **The frozen items are exactly frozen.** `sm_sgn` and `sm_pi_sgn` show **0** multiplier toggles above their
   zero — not "few", zero. `sm_e1`/`e16`/`e64` show 28–52 k, which is the exponent path's own `txfma_csa`
   instances (`txfma_csa` is instantiated in `txfma_e1`, `e2`, `e5` and `f3` as well as inside the tree's
   compressors), 0.7–1.2 % of a mantissa item's multiplier column.
2. **The stages are exactly additive.** `sm_sgnlo`'s vector equals `sm_lo12`'s plus `sm_sgn`'s to the last
   toggle, in MUL, in BACK, in f0+ctl and in the total (ratio 1.0000 in all four). So *in the RTL*, a flipped
   sign bit and twelve flipped mantissa bits cost exactly the sum of what each costs alone. Whether the
   **energy** is additive the same way is P2 below, and it is the single result the chain most needs: if it
   fails, no per-stage energy split exists and a linear toggles→watts model is wrong in principle.

## Power, and why the clock will hold

E64 measured aifoundry2 at 800 MHz: 35.0 W board on zeros, 82.2 W on random, with static B(800 MHz) = 33.61 W
and the governor regulating a ~1.3 s average of board power to 65 W. A random item would therefore throttle and
every price would be contaminated by the clock. Every item here runs on **512 minions** (`--per-shire 16`,
every shire), half of E60's and E65's 1,024, and the busiest (`sm_sp12`, ~31 % of random's toggle count) is
expected at **38–45 W** — the whole set stays well under 60 W. `anchor_zeros` and `anchor_pi` are lower still.
No built-in `randn` item is run on this card tonight for exactly this reason.

**The clock is a gate, not an assumption.** Every run's telemetry is checked for `mhz.minion == 800` over its
measurement window; a run with any off-800 sample in the window is dropped and counted in the results. The
per-item board maxima are reported.

## Protocol

- `hl/block.sh` (E60's, unchanged but for the two default-preserving knobs below), which holds `flock -n
  /run/lock/etsoc-shire0.lock` for the pass, puts every device process under `timeout 10` with `--stop-file`,
  stops at a 78 °C reading or on telemetry older than 3 s, writes `et-lab-manifest` and `gen.sha256` beside the
  data, and releases the lock between passes.
- **Two knobs added to E60's runner, both defaulting to the old behaviour** (`Q128(b)`): `HL_EXPN` names the
  experiment directory under `$DATA_ROOT` (so E68's passes do not land in E60's `hl/`), and
  `HL_SHIRES`/`HL_PER_SHIRE` reach `run_hl.py`'s new `--shires`/`--per-shire`, whose defaults are the literal
  `0xffffffff` and `32` the code had hard-coded. Nothing E60 or E65 ran changes.
- Launch reading: **`HL_TARGET=58`, `HL_PREHEAT=59`**, E60's pair, `HL_BURNIN=2`.
- Three passes (4, 5, 6 … numbered from 1 under `HL_EXPN=sm`), each an independent replicate with its own
  shuffle seed; `anchor_pi` first and last in every pass.
- Before the first launch: `et-boot-check --status`, `et-who`, `who`, `uptime`, and a `V3_DRY=1` dry run.
  The card is claimed in `#community-lab` before the first launch. If anyone else takes the card, stop and wait.
- Card time at most 1.5 h.

## Pre-registered analysis

Per run, P = mean board power over [t₀+1 s, t₀+3 s) corrected to the launch reading with the card's leakage
slope, exactly as `hl/reduce_hl.py` does it; gates on one clock (800 MHz), voltage within 3 mV of the pass
median, an on-protocol launch, and fma cycles per op within 0.5 % of the family's zero. **ΔP = item − its own
zero, per pass**; the unit of replication is the pass; SE from the between-pass scatter.

The stage split is the weighted least squares fit over the nine items

  ΔP_i = β_mul · MUL_i + β_back · BACK_i ,

with MUL and BACK the table above (in millions of RTL-name toggles per op), weights 1/SE², no intercept — the
zero subtraction already removed every fixed cost. β's are in W per million toggles per op per 512 minions;
their ratio is the quantity of interest and is free of the names-per-net factor as long as it is the same in
both columns (it is not exactly, and the limitation is stated with the result).

## Predictions, frozen with this commit

- **P1 — the multiplier's share.** For `sm_lo12`, s_mul = β_mul·MUL / (β_mul·MUL + β_back·BACK) lies in
  **[0.35, 0.85]**. The RTL's uniform-energy value is 0.668; the gate level says the multiplier is 0.11–0.13 pJ
  of a 745 fJ board flip (15–17 %), but the board number also carries the operand bus, the register file's read
  ports, the result path and the accumulator, all outside the unit, so the in-unit share must be higher.
  s_mul below 0.35 means the back end dominates and a Hamming-distance model keyed on the multiplier is wrong.
- **P2 — additivity (the structural test).** ΔP(`sm_sgnlo`) = ΔP(`sm_lo12`) + ΔP(`sm_sgn`) to within
  **max(2 SE, 10 % of ΔP(`sm_sgnlo`))**. The RTL says the toggle vectors add exactly; this asks whether the
  energy does. A failure falsifies any linear per-stage energy model, this one included, and is reported as the
  headline.
- **P3 — the frozen-multiplier floor.** ΔP(`sm_sgn`) > 0 at ≥ 3 SE: a flipped bit that never enters the
  multiplier still costs measurable energy. Its size relative to a mantissa flip, ΔP(`sm_sgn`)/ΔP(`sm_lo12`),
  lies in **[0.02, 0.25]** (the RTL net ratio is 0.073).
- **P4 — the partner buys nothing when the tree is frozen.** |ΔP(`sm_pi_sgn`) − ΔP(`sm_sgn`)| < **0.5 W** and
  < 25 % of ΔP(`sm_sgn`). E60 and E65 found a busy partner (A = π) costs about +11 % on *mantissa* flips; with
  the tree frozen the RTL says +1.0 %, so this is a clean contrast, and a large difference would mean the
  partner's cost is not in the tree at all.
- **P5 — the aligner ladder.** ΔP(`sm_e64`) > ΔP(`sm_e16`) > ΔP(`sm_e1`), each gap ≥ 1 SE, and
  ΔP(`sm_e64`)/ΔP(`sm_e1`) in **[1.2, 2.2]** (the RTL ratio is 1.59). This prices f3's shift distance directly:
  the three items are bit-identical in the tree and differ only in how far the aligner shifts.
- **P6 — position inside the mantissa.** ΔP(`sm_sp12`) > ΔP(`sm_lo12`) at ≥ 2 SE (RTL +31 % in nets), and
  ΔP(`sm_hi12`) > ΔP(`sm_lo12`) (RTL +12 %). Twelve bits are not twelve bits: this re-tests E65's A1 on a
  second card at a second clock, with masks instead of single bits.
- **P7 — the clock held.** Every kept run is at 800 MHz throughout its window and every item's board maximum is
  below 60 W. Runs that are not are dropped, counted, and named in the results.

## Decision rules

Each prediction is scored PASS / FAIL / UNDECIDED against its own stated band, in the results section of the
data README and in §E68 of `docs/findings/03-experiments.md`. UNDECIDED is used where an interval straddles a
band edge or a pass count is too small for the SE to mean anything (fewer than 3 kept passes for the item).
A block whose passes do not survive the gates is reported as not run, never re-registered.

## Files

| | |
|---|---|
| `make_sm.py` | the operand files and their designed flip counts; `--check` re-derives both and asserts the frozen significands and the mask-only differences |
| `predict_sm.py` | the RTL design matrix: the fma_toggle bench per item, by stage, minus each item's own zero |
| `reduce_sm.py` | the registered reduction: per-pass ΔP, the weighted fit, and P1–P7 |
| `README.md` | this file |
