# V3-HLP: the fp16 and int8 single-bit price lists (E79, Q130)

*Pre-registered Sat 31 Oct 2026 (week 44) before the Discord claim and the first measured launch; the predictions
are frozen in `predictions.json` with this commit. Any change after this commit goes in the Amendments section at
the end, dated, before the data it touches. Card: **aifoundry3 card 0 only**, 600 MHz, ~523 mV, TDP 0 — the
boot-time value `et-board-clock-guard` writes, which is never changed here. Horace hub Status item 9
("fp16 and int8"); the Q130 brief's E79.*

**The question.** E65 priced all 32 bit positions of an **fp32 B** operand (83–1,008 fJ per flipped bit) and E67
all 32 of **A** (153–1,440 fJ), on this card, at this clock and voltage. The blog's claim — that the *kind* of
number you multiply sets the power — cannot yet say anything about the two formats a real inference workload
actually uses. This experiment runs the same Hamming ladder on **fp16** (`TensorFMA16A32`) and **int8**
(`TensorIMA8A32`), both sides, every position, so the post can say which bits of an fp16 and an int8 operand cost
most to flip, beside fp32's.

## What is new, and what is a verbatim port

| Piece | Where it comes from |
|---|---|
| the ladder idea, the launch protocol, the gates, the per-pass unit of replication | E60 `tools/claims-v3/hl/README.md`, unchanged |
| the card lock, `timeout 10` on every device process, the other-user test, the sampler, STOP | `tools/claims-v3/lib.sh`, unchanged |
| `run_hlp.py` | `hl/run_hl.py` with **one** functional change: the launch takes the item's own `--type` from the manifest instead of a hard-coded `fp32` (the `ec` kind is dropped; E79 has no catalogue items) |
| `block.sh` | `hl/block.sh` with the hlp paths, no enercat preflight, and a read-only `ettelem config` at the start and end of every pass |
| `make_hlp.py` | **new**: the operand set, parameterised by format. Its fp32 reduction reproduces `make_hl.py`'s published counts (4,096 B / 2,048 A per multiply-add), asserted by `--check` |
| `reduce_hlp.py` | `hl/reduce_hl.py`'s recipe, re-written for per-item zeros across three formats, plus an **idle bracket** and 95% intervals from the between-pass scatter |

Nothing under `tools/claims-v3/hl/` or any other lane's directory is touched.

## The host's tile layout, read from its own source

`workloads/sparsity/host/main.cpp` — `makeTiles` packs the tiles and `fillValues`'s `file:` branch reads
**1,024 raw A bytes then 1,024 raw B bytes in the chosen type's layout**, before the per-type value code and for
every `--type`, so a tile file alone gives any kind of number in any format with no rebuild:

```
E    = 1 (fp32) | 2 (fp16) | 4 (int8)          elements of B per column per 64 B line
K    = 16 * E                                  the tile's depth: 16 | 32 | 64
A[i][k]      at byte  i * 64 + k * size        16 lines of 64 B; A row i = line i
B[p*E+e][j]  at byte  p * 64 + (j * E + e) * size
```

So for **fp16** the two K-terms of one column sit adjacent inside a 32-bit group (`j*4`, `j*4+2`), and for
**int8** the four do (`j*4 + e`). One 32-bit operand word holds E elements **of one column** — not of one row.
A tile file written in the fp32 layout and fed to `--type fp16` would flip entirely different bits, which is why
`make_hlp.py` packs by format and `--check` re-reads every file back through the same layout.

## The unit's stream order, and why the designed counts do not depend on the read width

The fp32 order is PRM 9.4's, as `hl/make_hl.py:issue_streams` states it: for each B row k, for each A row i, two
micro-ops (C columns 0–7, then 8–15); lane *l* gets `B[k][l]` then `B[k][8+l]`, and `A[i][k]` broadcast to all
eight lanes. Generalised to E elements per read (`make_hlp.py:streams`):

```
for each B line group g (K / Ew of them):
  for each A row i (16):
    for half in (0, 1):
      lane l reads B[g*Ew + e][half*8 + l], e < Ew
      every lane reads A[i][g*Ew + e],      e < Ew
```

with `Ew = E`. **The designed flip count is invariant to `Ew`.** The count is *operand element reads whose bit
differs from the previous read in the same lane's stream* — E65's counting rule — and the alternation is driven by
the `half` index (B side) and the row index `i` (A side), never by `e`; packing more elements into one read moves
the same number of differing element reads into fewer transitions. That matters because int8 takes **318** cycles
per 16×16×64 op against fp32's and fp16's **546** (`docs/findings/05-claims.md`, E36/E39), which says the int8
datapath reads wider than four bytes a lane, and this experiment does not need to know how much wider.
`make_hlp.py --check` proves the invariance by recounting every int8 item at `Ew = 8` and asserting the identical
total, and proves the port by reducing the same code to fp32 and getting make_hl.py's own numbers.

| | designed flips per multiply-add, 8 lanes, one bit per flipping element read |
|---|---|
| **B side** | 16 rows × K × 16 columns = **4,096** (fp32) · **8,192** (fp16) · **16,384** (int8) |
| **A side** | half of it: **2,048** (fp32) · **4,096** (fp16) · **8,192** (int8) |

The A side is half the B side in every format for E67's reason: the issue order holds an A word across both
halves, so an A word can only change every *second* micro-op. Every count is re-derived from the written files by
`make_hlp.py --check`, and the reduction divides each item by its **own** manifest count, so the A and B prices of
all three formats are per-flipped-bit numbers on one footing.

## The items (`manifest.json`; 65 items, 62 operand files)

| Family | What changes | Positions |
|---|---|---|
| `b16_<j>` | fp16: B's bit j alternates between the two column halves, A = 1.0 | 0–15 |
| `h16q`, `h16q_e7` | fp16 B-side zero: that base held constant in both halves. `_e7` is the exponent-7 twin bit 14 needs | — |
| `a16_<j>` | fp16: A's bit j alternates down the rows, B = 1.0 | 0–15 |
| `a16q`, `a16q_e7` | fp16 A-side zero: A constant, B = 1.0 | — |
| `b8_<j>`, `h8q`, `a8_<j>`, `a8q` | the same for int8 | 0–7 |
| `b16m2`, `b16m4` | fp16 additivity: bits {8,9} and {6,7,8,9} flip together | — |
| `b8m2`, `b8m4` | int8 additivity: bits {5,6} and {3,4,5,6} | — |
| `b16p_9`, `b8p_6` | the **layout control**: the same single flip with the flipping half XORed by the line-group parity, so the operand alternates under either nesting of (half, group) | — |
| `z16`, `z8` | the zeros anchor of each format (built-in `--values zeros`, no file) | — |
| `h32q`, `b32_22` | the **fp32 tie** on this recipe at E65's dearest B position | 22 |
| `anchor_pi` | the fp32 built-in π anchor E60/E65/E67/E70 used, first and last in every pass: drift, and a tie to their passes | — |

**Bases, and why.** Every item of one side and format shares **one** base word (E67's design tightening), so an
item minus its zero differs in the chosen bit alone. The base is a random significand at the exponent that keeps
both words normal (fp16 exponent 15, value in [1, 2); fp32 exponent 127); the B side uses a per-lane base vector
of eight such words, as E65 did, and the A side one word, as E67 did. Bit 14 is fp16's exponent MSB and exponent
15 → 31 is Inf, so that one position uses the exponent-7 twin of the same significand (7 ↔ 23, both normal) and
gets its own zero — exactly how E65 and E67 handled fp32's bit 30. int8 has no exponent: its bases are bytes of
popcount 4, so no single flip can make one zero. **Every operand element of every file is nonzero** (and normal,
for the float formats), because the unit gates a lane whose operand word is zero and the fp16 pseudo-code's
two-term update runs only when all four of a1, a2, b1, b2 are nonzero (`main.cpp:expectC`, `literal`).
**Corrected by amendment A5:** that PRM rule is a documentation bug, and the gate is **one 32-bit zero test** taken
when the tensor operand register is written, with one mask for the float unit and both integer units
(`external/core-et` `vpu_ctrl.v:1230`, `:817-839`, settled by Q130(g) at `d8d7e19e`). It changes nothing here —
every operand element of every file is nonzero, so every word is ungated under either rule — and the all-nonzero
design is now justified by the real gate rather than the manual's.

The base is a random significand rather than exactly 1.0 because E65's and E67's fp32 lists were measured on
random-significand bases, and the point of this run is a like-for-like comparison with them; the *partner* is
exactly 1.0 (and 1 for int8), as the brief asks.

## Protocol (one block = one pass = one independent replicate)

Unchanged from E60/E65/E67/E70, through `hlp/block.sh` and `hl`'s `lib.sh`:

- **Launch reading.** Before every run: 2 s random-fp32 heater launches until the mean minion-shire reading is
  ≥ 59 °C, then idle until it first shows ≤ 58 °C, then launch. A run whose reading is not reached is skipped and
  recorded, never launched off-protocol; three in a row stop the pass.
- **Runs:** 4 s. Two unrecorded `anchor_pi` burn-in runs start every pass. `anchor_pi` runs first and last in
  every block (drift = last − first); everything else is shuffled with `Random("<card>|<pass>|<pass>")`.
- **Safety:** every device process under `timeout 10`; sparsity launches with `--stop-file`; the pass stops at a
  78 °C reading, on a telemetry line older than 3 s, or when another user appears on **this card**; the card lock
  is held for the pass and released between passes. Heat carries over, which is exactly what the launch gate
  controls: nothing launches until the reading has come back down to 58 °C.
- **Telemetry:** `ettelem` at 10 Hz for the whole pass (board power, rails, clock, voltage, 34 shire sensors).
- **Card state, read only:** `ettelem config` at the start and the end of every pass (`config_start.json`,
  `config_end.json`). TDP must read **0** and the temperature threshold **65**; a different reading is reported.
  `run_e79.sh ident` additionally reads `et-lab-manifest` and the firmware revisions
  (`DM_CMD_GET_MODULE_FIRMWARE_REVISIONS` and four other `GET` queries) once, for the Horace hub's Status item 7.
  **No knob is written anywhere in E79.**
- **Departure D1** (E60's, kept): on aifoundry3 a user who is only logged in does not block — other lab users keep
  idle tmux logins there, and Q129's E74–E76 ran with them present. Another user on *this card*, any other user's
  device process, or an unreadable `et-holders` does block, failing closed.

**Card budget: at most 75 card-minutes.** Four passes are planned (~12 min each at 66 runs a pass), at least three
are required; the cut rule is in `predictions.json` (`card_budget`): stop after the pass in flight at 70
card-minutes or 19:00 PDT, whichever comes first, never below three. A rung with fewer than three kept passes is
reported as **unresolved** and takes no part in any scored rule.

## Pre-registered analysis (`reduce_hlp.py`)

1. **Per run** (one process of one item at one position of one pass): `t0` = the start of its first launch record;
   `P` = mean board power over `[t0+1 s, t0+3 s)`, corrected to the launch reading with the card's leakage slope
   (`P80 = P − k (T̄window − T_launch)`, 21 Sep's `p80`; `k` = the median within-run drift of runs that heat ≥ 1 °C,
   `--leak auto`); raw `[1,4)` kept as a check; the minion rail over `[t0+2, t0+4)`; **the idle bracket**
   `P_idle` = mean board power over `[t0−1.2 s, t0−0.2 s)`, the card idle at the launch reading after the approach
   has waited for it; the work completed inside the power window (launch records overlapping it, prorated), as a
   rate in minion-ops/s.
2. **Gates, per run** (every failure counted and reported): one clock, the card's own 600 MHz; the rail voltage
   within ±3 mV of the pass median; an on-protocol launch within 0.5 °C of the target; `cycles_per_op` within 0.5%
   of the item's **own** zero rung in the same pass (so fp16's 546 is never compared with int8's 318); every launch
   record `ok`. A pass is set aside when more than one of its runs fails a gate or its `anchor_pi` drifts more than
   0.3 W from first to last.
3. **Within a pass,** every item minus its **own** zero (`manifest.json: zero`).
4. **The price of a position** — counted the way E65 counted it:
   `e = (P(item) − P(zero)) / (designed flips per op × ops per second)`, computed **per pass** and then averaged
   over passes; the interval is `t(0.975, n−1) ×` the between-pass SE. The unit of replication is the pass, never
   samples inside one burst. Reported in fJ, with `C = 2e/V²` and `Q = CV/e` at the run's mean voltage, and with
   the minion-rail arm beside the board arm, never instead of it.
5. **The zeros rung** is quoted as switching over the idle bracket, `P(z) − P_idle`, and as a ratio to the h0
   rung's own switching `P(h0) − P_idle`.
6. **Additivity:** each multi-bit rung's ΔW over the sum of its own single-bit rungs' ΔW, per pass then averaged —
   the E70 test at low Hamming weight.
7. **The layout control:** the control item's price over the primary item's at the same position, per pass then
   averaged. The control's own designed count is 16/512 below the primary's, because the group-parity term cancels
   at every group boundary; the reduction divides by each item's own count, so the ratio is a per-bit ratio.
8. **Sensitivity:** every price is re-reduced at E71's measured aifoundry3 idle slope **0.3803 W/°C**
   (`--leak 0.3803`) beside the fitted slope, as Q129's leak-sensitivity lane did for E65/E67/E70. The fitted
   slope is the primary.

## Predictions (frozen in `predictions.json` with this commit)

The mechanism: A is Booth-recoded and *selects* partial products; B is per-lane and *feeds* the partial-product
muxes. A flipped bit's avalanche is as wide as the other operand's significand, so a narrower format should price
a flip lower roughly in proportion to its significand width — 11/24 = 0.458 for fp16, 8/24 = 0.333 for int8.

- **P1 (fp16's shape).** P1a Spearman ρ(bit, price) over fp16 B mantissa bits 0–9 ≥ **0.60**. P1b the mantissa's
  span ≥ **3.0×**. P1c **fp16 has no flat floor**: fp32's floor ran from the LSB to 13 bits below the significand
  MSB, and fp16's mantissa is only 10 bits deep, so bit 5 should already be dearer than bit 0 with disjoint 95%
  intervals — a test fp32's own list would **fail** (112 fJ at bit 1 against 100 at bit 5).
- **P2 (the width ratio).** price(dearest fp16 B mantissa bit) / price(this run's `b32_22`) ∈ **[0.25, 0.80]**,
  centred on 0.458; the same against E65's published 1,008 fJ as a secondary leg, and the A side against E67's
  1,440 fJ.
- **P3 (int8).** P3a Spearman ρ(bit, price) over int8 B bits 0–6 ≥ **0.60**. P3b price(bit 7) ≥ price(bit 6) minus
  the 95% half-width of the paired difference — the MSB of a two's-complement byte carries weight 128 *and* the
  sign correction, so it should not be the cheap one a float's sign bit is.
- **P4 (zeros).** (P(zeros) − P_idle) / (P(h0) − P_idle) ≤ **0.20**, per format.
- **P5 (additivity, against E70's law).** r₂ ∈ **[0.55, 1.05]**, r₄ ∈ **[0.35, 1.00]**, and r₄ ≤ r₂ + 0.10, per
  format.
- **P6 (the order).** The layout control's price over the primary's ∈ **[0.80, 1.25]**, per format. A failure means
  the registered stream order is wrong and every price in this experiment is reported with that caveat attached.
- **P7 (the tie).** price(`b32_22`) ∈ **[756, 1260]** fJ (E65's 1,008 ± 25%).
- **P8 (int8's size).** price(dearest int8 B position) / price(`b32_22`) ∈ **[0.15, 0.60]**, centred on 0.333.

Point predictions per position are in `predictions.json` (`point_predictions_fJ_per_flipped_bit`): fp16 B bit 9
**462 fJ**, fp16 B bit 0 **50 fJ**, int8 B bit 6 **336 fJ**, int8 B bit 0 **40 fJ**, and the ΔW each implies.

## Decision rules

- A rule whose inputs are unresolved (fewer than three kept passes) is reported as **not scored**, never as passed.
- **A failed registered prediction is reported as failed**, in the results table, with its measured value beside
  its band. No band moves after this commit; a departure is a dated amendment written before the data it touches.
- A price whose 95% interval contains zero is reported as a **bound**, not a coefficient, and is excluded by name
  from any ratio that needs a positive floor (E67's correction).
- If `ettelem config` reads a TDP other than 0 or a threshold other than 65 at either end of a pass, that pass's
  data is reported separately and not pooled.
- If the measured `cycles_per_op` is not 546 (fp16) / 318 (int8) / 546 (fp32) to within 0.5%, the format's whole
  list is reported as suspect: it would mean the launch did not run the op this experiment prices.

## Files

`make_hlp.py` (items, operand files, designed counts, `--check`), `run_hlp.py` (one pass), `block.sh` (the lib.sh
block), `queue_hlp.sh` (passes in a row), `run_e79.sh` (the stages: `setup`, `ident`, `smoke`, `go`),
`reduce_hlp.py` (the analysis above), `report_e79.py` (the results tables and the scored rules),
`predictions.json` (the frozen bands). The operand set is generated into `build/hlp-gen` on the box and
`--check`ed there before the first launch; its hashes go in every pass's `gen.sha256`.

## Amendments

**A8, Sat 31 Oct 2026, 10:13:39 PDT (commit `23197287`, 3 min 01 s before pass 7914's first launch at 10:16:40)** — **two more block-A passes, 7914 and 7915, of exactly the registered item
list.** Why: the registered drift gate set **pass 7912** aside — zero failed runs, `anchor_pi` drift 0.4105 W
against the 0.3 W bar — leaving block A with **three** kept passes, exactly the registered `min_passes` floor and
no margin for a second one. The decision is driven by a **gate outcome**, not by any price: the gate ran as
registered, the pass is not reinstated, and nothing about the analysis changes. Card budget after it: about 65 of
the 75 registered card-minutes. **The final reduction uses every pass that passes the gates and no pass is chosen
after the fact** — that is written here, before passes 7914 and 7915 exist, so it cannot be bent later.

**A7, Sat 31 Oct 2026, 10:13:39 PDT (commit `23197287`)** — **one reported quantity added; no band moves and no registered number
changes.** The registered idle bracket is the second before each launch, after the approach has waited for the
58 °C reading. Over block A's four passes it turns out to be **contaminated**: in a dense pass the previous run's
power tail can still be inside it, so the h0 switching figure it feeds moves from 10.75 W (one pass) to
9.49 W (four) in fp16 and from 4.32 W to 0.93 W in int8, and its spread is wide. The reduction therefore also
reports **P(zeros) − P(h0)**, which is paired per pass and needs **no** idle bracket at all, and the report leads
with it: it is the direct statement of what zeros buy in a format. **P4 is still scored exactly as registered**,
on the idle-bracketed ratio, and its spread is printed beside it; the contamination is reported as a limitation of
that bracket, not repaired after the fact.

**A6, Sat 31 Oct 2026, 10:13:39 PDT (commit `23197287`, while block B's last pass was running — it changes no count, no analysis and no measured number)** — **A4's structural wording replaced with the public RTL's own, its count
unchanged.** A4 inferred int8's micro-op structure from power alone and described it as "each lane reading the
eight contiguous bytes of columns 2*l* and 2*l*+1". `external/core-et` says it exactly, and says it better:

- **`VPU_NUM_TIMA 2`** (`rtl/inc/vpu_defines.vh:210`) — **two** integer tensor units per lane, instantiated in a
  `genvar` loop (`vpu_lane.v:408`, `LANE_TIMA`), against **one** float tensor FMA unit whose B column selector
  `dc_read_b_col` is a single bit (`vpu_tensorfma.v:282`, "Which B col we are about to request").
- **`TIMA_INT8_MUL_NUM 4`** (`rtl/inc/tima_defines.vh:8`) — each integer unit takes a **32-bit** operand and makes
  four int8 products, summed in one adder (`tima/tima_top.v`, `F2_PROD` and `f2_prod_add`).

So **8 lanes × 2 units × 4 multipliers = 64 int8 multiply-adds a cycle**, and 16,384 / 64 = **256** cycles of
work, against the float path's 8 lanes × 1 unit (× 2 K-terms in fp16) = 16 MACs a cycle, **512** cycles. The
measured totals are 318 and 546, so the fixed overhead is **62** cycles for int8 and **34** for the float path:
the work accounts for 256 of 318 and 512 of 546, and **this amendment does not explain the 28-cycle difference
between the two overheads**. That is the first *mechanism* this repo has for the
546 / 546 / 318 the ablations have measured since E15 and E36: **int8 is faster because it has twice the units,
each four multipliers wide.** The consequence for E79 is what A4 measured: in int8 a given (lane, unit) pair always
drives the **same** C column, because both halves issue in the same cycle, so a flip placed on the column-half
boundary never alternates in time — 0.003 W. **The designed count does not move:** 16 line-group transitions ×
(8 lanes × 2 units) × 4 int8 elements = **1,024** changed element reads per multiply-add per flipped bit, the same
number A4 registered by the other route, so every int8 B price stands as reduced.

**A5, Sat 31 Oct 2026, 10:13:39 PDT (commit `23197287`)** — a **citation correction only**, written while block B was still
running, which is safe because it touches no data: it changes no item, no count, no band, no analysis and no measured number. The registration
justified its all-nonzero operands partly by the PRM's fp16 rule that the two-term update happens only when all
four of a1, a2, b1, b2 are nonzero. Q130(g) settled the gate from the public RTL that morning (`d8d7e19e`): there
is **one 32-bit zero test**, taken when the tensor operand register is written, and **one mask drives the float
unit and both integer units** (`external/core-et` `vpu_ctrl.v:1230`, `:817-839`); the PRM rule is a documentation
bug, which E39 had already measured. The format therefore only sets how many numbers ride in a gated word — one
fp32, two fp16, four int8 — so a zero is worth most in fp32 and least in int8. **E79's design is unaffected**:
every operand element of every file is nonzero, so every word is ungated under either rule. The two justification
sentences now cite the gate instead of the manual. E79's own P4 result is an independent silicon measurement of
that conclusion (Result 6).

**A4, Sat 31 Oct 2026, 09:49:45 PDT (commit `4216f1fb`)** — written after pass **7910** and **before any data it touches** (block B,
passes 7920–7923). Pass 7910 produced two measured facts the registered design did not anticipate, and A4 adds the
items that resolve them. **No registered band moves, and P6 is scored on block A's data exactly as registered —
it fails, and the failure is reported as a failure.**

*Fact 1 — int8's B-side `jg` ladder does not alternate at all.* Every int8 B single-bit rung reads
**0.003 ± 0.02 W** above its zero, where the identical construction reads **4.73 W** in fp16 and **5.00 W** in
fp32. int8 takes **318** cycles per 16×16×64 multiply-add against 546, which is **256** micro-ops, not 512: one
micro-op covers all sixteen C columns, each lane reading the eight contiguous bytes of columns 2*l* and 2*l*+1 at
K-terms 4p…4p+3 (8 lanes × 2 columns × 4 K-terms = 64 MACs a micro-op; 256 × 64 = 16,384 = 16·16·64). Under that
structure a lane's two columns **never change**, so a flip placed on the column-half boundary never enters the
stream, and what is left is a static operand-content difference — which is what 0.003 W is. The 546-cycle formats
do have the half index and do alternate, which is why they read 4.7–5.0 W. *So the 318-cycle structure is measured,
not assumed.* **Added:** the `kg` layout, which carries the flip on the line-group parity alone, the same in every
column, and is the only one of the three that alternates in int8 — `b8k_0` … `b8k_7`, the int8 B price list.
Its designed count is the closed form the structure implies, **1,024 changed element reads per multiply-add per
flipped bit** (16 line-group transitions × 8 lanes × 8 elements), written into the manifest with the generic
model's count kept beside it in `flips_generic` so the number can be re-divided if the structure is ever shown to
be different.

*Fact 2 — two layouts of the same flip, at the same designed count, differ 5.4×.* `b16p_9` (the registered layout
control, 7,936 designed flips) reads **0.880 W** where `b16_9` (8,192) reads **4.725 W**. The designed flip count
therefore does **not** determine the step, and **P6_fp16 fails**. Two more measured facts frame it: the multi-bit
rungs are deeply saturated (1 bit 4.73 W, 2 bits 5.33 W, 4 bits 6.18 W), so the **marginal** cost of a further
flipped bit is about **46 fJ** against the 515 fJ a single-bit rung reports against a constant zero — E67's
amendment A13 argument (a price measured this way is `T + e·n·rate`) with `T` dominant. The mechanism this points
at is the **result path**, not the multiplier: in the `jg` layout the two C columns a lane alternates between
accumulate *different* products (one sums the base, the other the base with the bit flipped), so the result bus
swings by the accumulated difference every micro-op; in `jgp` and `kg` the two columns see the same mix and stay
nearly equal. **Added, to test exactly that:** `b32p_22` (the same `jgp` control in fp32, where E65's published
1,008 fJ is the independent anchor), `b32k_22` and `b16k_9` (the `kg` probe in fp32 and fp16). The reduction gains
an **order probe** block reporting the three layouts' raw ΔW and their order-free ΔW ratios — they divide by no
designed count — and a **marginal** block reporting (ΔW(4-bit) − ΔW(2-bit)) per extra flipped bit. Both are
reported quantities; neither moves a band, exactly as E67's A13 and A14 added quantities beside their registered
ones.

*Block B, four passes (7920–7923), 20 items, ~3 min a pass:* `anchor_pi`, `h32q`, `b32_22`, `b32p_22`, `b32k_22`,
`h16q`, `b16_9`, `b16p_9`, `b16k_9`, `h8q`, `b8_6`, `b8p_6`, `b8k_0` … `b8k_7`. Operand set `build/hlp-gen2`;
**every one of the 62 operand files block A ran is byte-identical in it** (62 of 62, checked before the first
block-B launch), so nothing already measured changes. Card budget after block B: about 56 of the 75 registered
card-minutes.

*How the lists are quoted, given P6's failure.* The fp16 and fp32 single-bit prices stay as measured and are
labelled **all-in against a constant-operand zero, in the `jg` layout** — the same quantity E65 and E67 published,
on the same card, so the comparison the brief asks for is like-for-like. The **marginal** price is reported beside
every list, and the order probe's ΔW ratios are reported as the evidence that the two are far apart. No price is
quoted as "the energy of a flip" without that pair.

**A1, Sat 31 Oct 2026, 09:31:52 PDT (commit `e66f7c1a`)** — written during pass 7910 and **before any data it touches** (passes 7914
onward). *Four more passes, 7914–7917, of exactly the registered item list.* Why: a pass takes about **4.5 min**,
not the ~12 min budgeted, because the card idles at 50 °C today, so the approach to the 58 °C launch reading is
instant (`0 heats and 0.1 s` in every run of pass 7910) and a run costs its 4 s plus ~0.3 s of overhead. Eight
passes fit inside the registered 75 card-minute budget with room to spare, and the dominant uncertainty in every
price is the between-pass scatter, which is what more passes reduce. **Nothing else changes:** the item list, the
operand files, the launch protocol, the gates, the analysis and every registered band are as committed in
`2a72d352`. The `min_passes` floor of 3 and the stop rule stand.

**A3, Sat 31 Oct 2026, 09:32:31 PDT (commit `270d2108`)** — written during pass 7910 and before any data it touches. **A1's four extra
passes are cut to two: 7914 and 7915, six passes in all.** Why: A1's 4.5 min figure came from pass 7910's first 17
runs, where the approach was instant; by run 24 the card has warmed and the wait for 58 °C costs 1–3 s, so the
measured pace is **8.7 s a run — about 10 min a pass**. Eight passes would be ~82 card-minutes, past the
registered 75-minute budget; six are ~63, plus the smoke and the identity read. The budget is the binding
constraint and it is not moved. Nothing else changes.

**A2, Sat 31 Oct 2026, 09:31:52 PDT (commit `e66f7c1a`)** — the same commit, same reason, no data touched: `collect_e79.sh` is added
(it reduces every finished pass, runs the registered E71-slope sensitivity arm and assembles the data directory).
It is plumbing around the already-registered `reduce_hlp.py` and `report_e79.py` and changes no analysis.
