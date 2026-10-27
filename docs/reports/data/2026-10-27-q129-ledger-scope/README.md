# What the board pays besides the arithmetic — the lane's register files, operand bus and result path (Q129)

27 October 2026, on aifoundry1 (desk compute only; **no card was used**). The flow and how to
re-run it: [`tools/open-flow/scope/`](../../../../tools/open-flow/scope/README.md). The method, the
two models and the things that bound the answer: [`METHOD.md`](METHOD.md).

🛑 **Amended the same day, after an adversarial verification. Every measurement reproduced; seven
readings of those measurements did not, and five moved a published number.** (1) The 0.654 pJ
zero-operand floor is **34% clock and 66% signal switching**, not "the clock gates" — the
accumulator index sweeps in every pattern, on a card too — so the bottom of the range is
**1.26 pJ, not 0.54** (§2, §6). (2) The card's own `zeros` measurement **puts the register-file
model above what the board permits**: it is not an open-ended ceiling, it over-prices, and the
claim that the result path closes is withdrawn (§2, §4). (3) The index-alone bound priced counted
bits at a per-*designed*-flip slope; refitted it is **166–175 fJ**, not 72–136, which reverses the
conclusion drawn from it (§4). (4) The two benches count the same operand files' bus bits
differently (−26% to +40% per rung), so §3's per-bus-bit sum is given on both denominators.
(5) The data-dependent `+internal` figure is differenced, not scaled: **0.518**, was 0.544 (§6).
(6) TENC's zero is the bench's tie-off, not an independent confirmation of the RTL (§2).
(7) §1 and §6 carry the range rather than its top. **Unchanged:** the per-part table, the census,
the ladder rung energies, both controls, the cap coverage, and the tool-version identity with the
arithmetic run that lets the two ledgers add. The amendments are listed with their before/after in
"What was registered, and what happened".

**Why.** Q128's chain says the bottom-up ledger of one random fp32 multiply-add is a floor three
times over, and the third reason is a scope one: *"the ledger covers one lane's arithmetic while the
board pays for the register file's read ports, the operand bus, the result path and leakage"*
([`../2026-10-27-transistor-ledger/README.md`](../2026-10-27-transistor-ledger/README.md) § Why the
bottom-up number is a floor). This directory prices that scope. Same RTL source (public `core-et`,
branch `erbium`, sha `b38a1a31`), same open 7 nm library (ASAP7 RVT, TT), same flow, same operand
files, same 0.517 V — so the two numbers add.

---

## Results

### 1. The lane's transport is not a correction term

| per random fp32 multiply-add, one lane | pJ |
| --- | ---: |
| the arithmetic (`txfma_top`), switching — Q126(e) | 1.516 |
| **the transport (this netlist), switching** | **1.033** |
| the arithmetic, + the cells' internal energy | 1.946 |
| **the transport, + the cells' internal energy** | **1.484** *(upper)* |
| the same less its clock-net energy — the part no idle subtract can contain | 1.261 *(lower)* |
| **the two together** | **3.21 – 3.43** |
| E38/E39 at the board, over idle, three-card mean | **5.783** |
| the same at the minion rail (×0.750, E60's measured ratio) | 4.337 |
| **closure, was (arithmetic alone)** | **34% of the board, 45% of the rail** |
| **closure, now** | **55–59% of the board, 74–79% of the rail** |

*(Rail figures on Q128's 4.337 pJ. On Q129's own corrected rail footing, 4.77 pJ, the rail closure
is 67–72% — §6's last paragraph.)*

The answer is a **range** because 0.223 pJ/MAC of the transport is clock-net energy that may
already sit inside the idle E38 subtracts, and because the big part of it is a model that §2 shows
is over-priced. §6 has the arithmetic; the numbers in this table are the end points, not a
best estimate.

And it is not a correction term in silicon either — on the same library and flow, one lane's
transport is **larger than one lane's arithmetic**:

| | cells | transistors | area µm² | flip-flops | latches | clock-pin cap fF |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| the arithmetic, `txfma_top` (`census_mixed.json` of Q126(e)) | 15,805 | 159,896 | 2,126.1 | 1,974 | 13 | 945.0 |
| **the transport, this netlist** | **21,608** | **200,504** | **2,532.4** | **340** | **3,540** | **1,844.0** |
| ratio | 1.37× | 1.25× | 1.19× | 0.17× | 272× | 1.95× |

🛑 **Most of that size is one of the two models, and it is an upper bound — a card measurement
says a violated one.** The 64 × 32 3-read 2-write VPU register file is a compiled macro the open
library cannot build; it is replaced by core-et's own **latch array** (`rf_latch_3r_2w`) at the
same geometry, which is 15,685 cells and 1,718 µm² for 2 kbit — roughly an order of magnitude more
area than a compiled macro would take. Read the model rows as a **ceiling** on what the register
files can account for, where the rest of this ledger is a floor — and see §2, where the board's own
`zeros` figure puts that ceiling *above what the card permits*.
[`METHOD.md`](METHOD.md) § "The two models, and which way they are wrong".

### 2. Per part

Switching energy per random multiply-add, one lane, ASAP7 RVT TT, 0.517 V, from
`power-mixed/power_gr_randn.json`. "data-dependent" is `randn` − `zeros`: what the part costs
because the operand *words* move. The next column is the `zeros` run itself — **renamed from
"clocked floor", because it is not one**: the micro-op stream is the same in that run and the
accumulator index still sweeps 2 i + h, so most of it is signal switching, not clock. Its own
clock/signal split is in the table note below. `M` marks a model. Every row charges this one lane
in full (§7 on the convention).

| part | pJ / MAC | data-dep. | zero-operand | + internal est. | signal toggles / MAC | cells | seq. bits | M |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :-: |
| VPU register file array, 64 × 32 3r2w | **0.4815** | 0.1765 | 0.3050 | 0.3177 | 2,673.2 | 15,685 | 2,243 | **M** |
| top-level nets, the clock root, the control's ports | 0.3676 | 0.1114 | 0.2562 | 0.0264 | 222.4 | — | — | — |
| operand bus + F4…F8 result pipeline (`vpu_bypass`) | **0.1349** | 0.0550 | 0.0799 | 0.0795 | 669.3 | 2,306 | 190 | — |
| VPU register file collision bypass (`vpu_rf`) | 0.0353 | 0.0319 | 0.0035 | 0.0191 | 160.5 | 585 | 99 | — |
| tensor A register file, 32 b × 2 *(shared by 8 lanes)* | 0.0068 | 0.0032 | 0.0036 | 0.0045 | 37.6 | 176 | 101 | — |
| tensor B register files, 32 b × 4, ×2 | 0.0060 | 0.0008 | 0.0052 | 0.0036 | 29.9 | 688 | 334 | — |
| TIMA accumulator file, 32 b × 16 | 0.0003 | **0.0000** | 0.0003 | 0.0002 | 2.0 | 1,344 | 562 | **M** |
| tensor TMP register file, 32 b × 8 *(shared by 8 lanes)* | 0.0003 | 0.0000 | 0.0003 | 0.0002 | 2.0 | 681 | 299 | — |
| per-lane control pipeline | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.1 | 73 | 52 | **M** |
| **total** | **1.0329** | **0.3788** | **0.6540** | **0.4512** | **3,797** | **21,538** | **3,880** | |

The cell column sums to 21,538 of the netlist's 21,608: the other 70 are top-level tie and buffer
cells that belong to no block. The two model register files hold 2,805 of the 3,880 sequential bits
and 17,029 of the 21,538 cells, which is the size of the substitution in one line.

**The zero-operand column's own split: 0.2231 pJ clock nets (34%), 0.4310 pJ signal (66%).** All
0.2231 pJ of the clock is in the top-level row (the clock root and the arrays' gated branches);
every other row's zero-operand figure is **entirely signal switching** — the register-file array's
0.3050 pJ has 0.0000 pJ of clock in it. The committed `power-mixed-clkwide/` run, which widens the
clock regex to catch `clk_rf_wr[i]`, `clk_wr_data_a_n` and `enclk`, moves the split only to
0.2301 / 0.4240, so this is not a regex artefact. *(`ledger-scope.json` → `gap.zeros_*`.)*

Five things fall out, and the first two are the ones that matter:

- **the accumulator's register file is the single biggest item in the transport, 0.48 pJ per
  multiply-add on this model — 47% of the transport and a third of the whole new ledger.** It
  reaches that on 2,673 signal toggles per multiply-add, nearly as many as the arithmetic's whole
  3,299, because a 64-entry 3-port read path is a 64:1 mux tree per bit per port and the
  accumulator's index moves every cycle. **This is the model, so it is a ceiling**; a compiled
  macro reads through bitlines and would cost less. Nothing in this project has measured that
  number, and until something does, "the register file's read ports" is bounded between 0 and
  0.48 pJ per multiply-add, not estimated;
- 🛑 **and the card says that ceiling is too high to be true.** E38 ran the same instruction
  stream with zero operand data and the **whole board** cost **0.27 pJ per multiply-add over
  idle** (three-card registered mean; per card 0.1633 / 0.4034 / 0.2512 — Q128 `data.json`
  → `/permac/mean_zeros_pJ`). This netlist's `zeros` run is that stimulus, and *one lane's
  transport* claims **0.6540 pJ** there — **2.42× the whole board**, 1.60× it counting only the
  0.4310 pJ signal part, and the register-file array row **alone** (0.3050 pJ, all signal) is
  1.13× it. The comparison holds whichever way the idle subtract falls: if the lane's clocks run
  at idle the card figure excludes clock and the 0.431 pJ signal part is what must fit inside
  0.27 pJ; if they are gated at idle, the whole 0.654 pJ must. So the latch array is not an
  open-ended ceiling with "nothing below it but zero" — **it is demonstrably above what the board
  permits**, and over-pricing is the first thing to suspect wherever a number from it lands near
  its card counterpart (§4, the result bit). E74 (register-file cells), or a compiled-macro energy
  figure, is what replaces it with a measurement. *(`ledger-scope.json` → `gap.card_zeros_bound`.)*
- **the operand bus and the result path cost 0.135 pJ per multiply-add**, and that figure is an
  **open-netlist result, not a model**: `vpu_bypass` is the real core-et module, 2,306 ASAP7 cells
  and 190 flip-flops, and all three source muxes and the five pipeline stages are in it;
- **the int8 accumulator file costs nothing on an fp32 multiply-add — 0.0000 pJ data-dependent.**
  `vpu_tensorc_rf` has 1,344 cells and 562 latch bits sitting in every lane, and an fp32
  TensorFMA32 never reads or writes it: every port `vpu_tensorfma.v` gives it is TIMA-prefixed.
  🛑 **That is the RTL reading, and the run does not independently confirm it**: `tb_scope.sv`
  ll. 49–52 tie `tenc_wen`, `tenc_ren`, `tenc_waddr`, `tenc_raddr` and `tenc_wdata` to zero and
  never assign them again, following the same RTL reading, so a data-dependent zero is a property
  of the stimulus. What the run *does* measure is the price of carrying the block anyway:
  **0.0003 pJ per multiply-add** of clocked cost for 1,344 idle cells, and 562 latch bits of clock
  load in every lane. An independent check would drive TENC's ports from an fp32 stream and show
  the unit's own control never raises them;
- **0.654 pJ of the transport's switching survives with every operand word zero — 63% of it — and
  only a third of that is clock.** 0.2231 pJ is clock-net energy (the clock root and the latch
  arrays' gated branches); the other 0.4310 pJ is signal switching, because the accumulator's
  index sweeps 2 i + h in every pattern (`sim_acct.txt`: `idx_toggles` = 992 per op in **all 15
  runs**, `zeros` included) and a 64-entry read mux tree switches on the index whether or not the
  data moves. **A card performs that sweep too**, so that switching cannot be inside an idle
  subtract — which is why §6's lower reading removes the clock nets only. The clock part is still
  the most inflated number in the table: on the model's arithmetic it is dominated by the latch
  array's 64 per-entry clock gates.

### 3. One flipped operand bit: 42–53% of the board, against 27–30% before

The same Hamming-ladder operand files E60 ran on three cards, fitted the way E60's own reducer fits
them — a line over h ≥ 1, free intercept — first against the *designed* flip count, then against
the counted operand-bus bits (E60's own amendment-A2 regressor). The arithmetic's slopes are
Q126(e)'s; the transport's are this netlist's; the board column is E60's **aifoundry3** block
(600 MHz, 521.8 mV, 4 passes). The two tables bracket the answer at 42–53% of the board on
switching alone: the headline range is theirs, not one of them.

| | arithmetic | **+ transport** | = sum | E60 at the board | at the rail (×0.75) | closure vs board | **vs rail** |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `lq` (quiet partner A = 1.0), switching | 32.9 | **16.4 ± 9.3** | **49.3** | 116.7 ± 0.6 | 87.6 | 42% *(was 28%)* | **56%** |
| `lq`, + the cells' internal | 46.3 | 21.0 ± 11.9 | 67.3 | 116.7 | 87.6 | **58%** | **77%** |
| `lb` (busy partner A = π), switching | 38.5 | **25.4 ± 6.4** | **63.9** | 129.9 ± 0.5 | 97.4 | 49% *(was 30%)* | **66%** |
| `lb`, + the cells' internal | 54.9 | 32.2 ± 7.8 | 87.1 | 129.9 | 97.4 | **67%** | **89%** |

Per **counted operand-bus bit** (E60's amendment-A2 regressor), where the fit is better resolved —
🛑 **but the two benches do not count the same operand files the same way, so the sum has to be put
on one denominator before it is added.** On the same files the scope bench's `bus_toggles` run
from 0.74× the arithmetic bench's (`lb_h1`) to 1.40× (`lb_h8`), with `randn` the one pattern where
they agree (17,394 against 17,349, 0.3%) — the cross-check the first version of this file quoted.
Both fits, against the same board number:

| per counted bus bit | transport | arithmetic | = sum | E60 board | closure vs board | + internal, vs rail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lq`, on the **arithmetic bench's** counts *(like for like)* | **11.2 ± 4.3** | 20.0 | **31.2** | 74.7 | **42%** | 76% |
| `lq`, on the scope bench's own counts | 10.9 ± 2.7 | 20.0 | 30.9 | 74.7 | 41% | 75% |
| `lb`, on the **arithmetic bench's** counts *(like for like)* | **18.2 ± 4.4** | 27.5 | **45.7** | 85.6 | **53%** | 97% |
| `lb`, on the scope bench's own counts | 12.1 ± 1.1 | 27.5 | 39.6 | 85.6 | 46% | 85% |

The denominator is worth 7 points of `lb` closure and nearly doubles the slope's standard error,
so the like-for-like rows are the ones to quote and the per-rung divergence is tabulated in
[`METHOD.md`](METHOD.md) § The stimulus. `lb` + internal reaching 97% of the rail is **not** a
closure claim: it is a 18.2 ± 4.4 fJ slope added to a figure fitted on a netlist whose
register-file write port is the over-priced model (§2).

🛑 **The `lq` designed-bit slope is not resolved, and the ladder is not monotone on this netlist.**
`lq` runs 0.734, 0.760, 0.867, **0.848** pJ at h = 1, 2, 4, 8: h = 8 is *below* h = 4, so the
standard error of the slope (9.3 fJ on 16.4) is 57% of it. `lb` is monotone except at h = 4 (0.739,
0.802, **0.787**, 0.934) and reads 25.4 ± 6.4. The transport's per-bit price depends on *which* bits
move, not just how many — a B-mantissa bit enters through TENB's 4-entry read and one mux, while the
accumulator's bits come through the 64-entry array — so a Hamming count is the wrong regressor for
it. The like-for-like bus-bit rows above are the ones to quote; the designed-bit column is carried
because that is the column E60 published, and its unit (fJ per *designed* flip) is not
interchangeable with a per-counted-bit price — §4 made exactly that substitution and had to be
corrected for it.

### 4. The result bit, and the register index: the two E60/E61 numbers that have a counterpart now

Both are differences against a control that holds one field still, "everything else the same"
(`+resfix`, `+accfix`). **Both are composites**, and that is the point: the control cannot move one
field in isolation, and neither could E60's or E61's card design.

| | bottom-up, transport | what the difference contains | board | at the rail | closure vs rail |
| --- | ---: | --- | ---: | ---: | ---: |
| **a result bit** | **23.58 fJ** (31.46 with internal) | 13.80 result bits/MAC through the F8 mux, the register-file write, **and the accumulator read-back they cause** | E60 **31.17 ± 0.17 fJ** (`xnz`) | 23.4 fJ | 🛑 **101% — read the bullet** |
| **a changed read index** | **252.4 fJ** (440.2 with internal) | 1.94 index bits/MAC **and the 13.75 accumulator-word bits the new index selects** | E61 **369–452 fJ** | 277–339 fJ | **74–91%** |

- 🛑 **The result bit reads 101% of its card number, and the leading explanation is that the model
  over-prices it — not that the result path closes.** 23.58 fJ per result bit bottom-up against
  23.4 fJ at the minion rail would be the first **energy** rung in this project's chain to meet a
  card measurement rather than fall short of it, and that is exactly why it should not be leaned
  on: the result bit's path runs through the **write port of the register-file model**, and §2
  shows that model costing 2.4× the whole board's `zeros` figure for one lane. A bottom-up number
  that exceeds the card elsewhere in the same netlist is the simplest reason a bottom-up number
  here *reaches* the card. **The claim "the result path closes" is withdrawn** until E74 replaces
  the model with a measurement; what stands is that the result path's bottom-up price is of the
  right order and bounded above by about 23.6 fJ per bit.
  It is also the composite above, not the write side alone: this design cannot separate the result
  word from the accumulator read-back it causes one pass later.
- **The register index does not close, and E61 said it would not.** E61 scored its own
  register-index ladder **under-resolved — "369–452 fJ per index bit, 12–14 times the page's 32 fJ,
  with no linear law across the three matched-rate rungs"**. The bottom-up composite is 252 fJ per
  index bit, 74–91% of E61's figure at the rail, so the card number is the right order.
  🛑 **Corrected: most of that composite is the index term itself, not the data it selects.**
  Subtracting the 13.75 *counted* accumulator-read bits at the transport's own fitted
  **per-counted-bus-bit** slopes (10.9 / 12.1 fJ) leaves **166–175 fJ per index bit — 66–69% of the
  composite**. The first version of this file priced those counted bits at the *designed-bit*
  slopes (16.4 / 25.4 fJ per designed h-flip), a different unit and the regressor §3 itself calls
  unfit, which gave 72–136 fJ and the opposite reading. On the arithmetic bench's bus counts the
  bound is 123–173 fJ, so the conclusion survives the denominator question in §3 at its lower end.
  This **strengthens** E61's "under-resolved" verdict rather than explaining it away: a card ladder
  that moves an index also moves a register's worth of data, and on this netlist the index wiring
  is the larger half of what it measured. Still a bound, not a measurement, because an accumulator
  bit read through the 64 × 32 array does not take the path a B-mantissa bit takes.
  *(`ledger-scope.json` → `controls.register_index.index_alone_fJ_per_bit_bounds_by_regressor`.)*

### 5. The clocked bits: 602.5 is an inside-the-arithmetic count

Q126(b)'s **602.5 register bits clocked per multiply-add** is counted inside `txfma_7s` only — the
83 `libs/registers` instances `ff_acct.sv` stands in for, 838 bits of the unit's 2,071. **None of
the 3,880 sequential bits in this netlist are in that scope**, so the transport's clocked bits are
*additional* to the 602.5, not part of it. This netlist carries 340 flip-flops and 3,540 latch bits
behind its own clock gates, and 1,844 fF of clock-pin capacitance against the arithmetic's 945 fF —
**1.95× the arithmetic's clock load, on the model**. Any load model that prices a multiply-add by
`ff_clocked` from that bench is pricing a third of the lane's sequential bits.

### 6. What moves in the waterfall, and what does not

| | pJ per random multiply-add | share of the 3.837 pJ **board** gap | share of the 2.391 pJ **rail** gap |
| --- | ---: | ---: | ---: |
| **upper reading** — the whole transport netlist, + internal | **1.484** | **38.7%** | **62.1%** |
| **lower reading** — the same less its clock-net energy, + internal | **1.261** | **32.9%** | **52.7%** |
| the lower reading under the wide clock regex (`power-mixed-clkwide/`) | 1.252 | 32.6% | 52.4% |
| *separately:* the part that moves with the **operand words** (`randn` − `zeros`), + internal | 0.518 | 13.5% | 21.6% |
| of which **open netlist, no model at all**: `vpu_bypass` + `vpu_rf`'s own bypass + TENA/TENB/TMP, + internal | **0.290** | **7.6%** | **12.1%** |
| the same, data-dependent part only | 0.144 | 3.7% | 6.0% |
| TIMA accumulator file, on the fp32 path | 0.000 | 0% | 0% |

**The honest answer is a range, and it is 1.26–1.48 pJ.** The upper reading charges the card for
the whole netlist. The lower one removes **the clock nets only — 0.223 pJ/MAC** — because that is
the one part of this netlist's cost an idle subtract could already contain: it is the trap
[`../2026-10-27-transistor-ledger/README.md`](../2026-10-27-transistor-ledger/README.md) flags for
the `zeros` pattern (*"the open flow's figure is the ungated root of this lane's clock tree, which
on a card is already inside the idle the measurement subtracts. 🛑 Do not quote it as closure"*),
and that trap is about the **clock tree**, not about everything a zero-operand run costs.

🛑 **The first version of this file set the bottom of the range at 0.544 pJ, the data-dependent part
alone, and that was wrong twice over.** First, it discarded the 0.431 pJ of signal switching the
`zeros` run performs — the accumulator index sweep, which a card performs too, and which no idle
subtract contains (§2). Second, it scaled the switching difference by the whole-design `+internal`
ratio instead of differencing it; power.py's internal estimate is a constant per signal transition,
so the differenced figure is 0.518 pJ, not 0.544. That line is now reported as its own quantity —
how much of the transport moves with the operand words — and not as the bottom of the range.

So in Q128's words: **the ledger moves from 1.946 pJ to between 3.21 and 3.43 pJ, and the closure
from 34% to between 55% and 59% of the board** (45% → 74–79% of the rail). The unaccounted 3.837 pJ
falls to between 2.58 and 2.35 pJ.

What the range does **not** span is the model question. Both end points contain the register-file
model's 0.48 pJ/MAC, which §2 shows is above what the card's own `zeros` figure permits; a true
accounting therefore sits below the bottom of this range by whatever that model over-prices, and
only E74 can say by how much. The measurement that would collapse the *range* is different again:
whether the lane's register files are clock-gated at idle on silicon, which decides the 0.223 pJ.

**Every rail figure on this page uses Q128's 4.337 pJ** (board × 0.750). Q129's own rail ledger,
published the same day, puts the minion rail at **4.77 pJ, band 4.55–4.95** on a corrected leakage
footing ([`../2026-10-27-q129-rail-ledger/README.md`](../2026-10-27-q129-rail-ledger/README.md)).
On that footing the rail gap is 2.82 pJ rather than 2.39, and this directory's rail numbers become:
transport names **44.7–52.6%** of the rail gap (from 52.7–62.1%), closure **67–72% of the rail**
(from 74–79%). The board numbers are untouched. Which footing the chain carries is Q128's call, not
this directory's; both are stated so the substitution is one line.

### 7. Why this is still a floor, and one new reason

Everything [`POWER.md`](../2026-10-26-open-netlist/POWER.md) says of the arithmetic's figure holds
here, and one of the three is worse:

1. **Only 37.0% of this design's capacitance is priced** — 21.8 of 59.0 pF — against the
   arithmetic's 50.5%. The unpriced 63% is the nets CTS and `repair_design` made after the netlist
   was simulated. They switch. *(`ledger-scope.json` → `totals.cap_fraction_priced`.)*
2. **No coupling term.** Detailed routing did not close on either scope netlist, same
   `DRT-0255` family as Q126(e)'s ten configurations, so the between-cell wire is a global-route
   Steiner estimate — a lower bound on every wire.
3. **No glitch factor.** Unchanged blocker.
4. **The internal-energy estimate covers combinational transitions only.** On a netlist that is
   3,540 latches and 340 flip-flops, the sequential cells' own clock-pin internal energy — skipped
   here — is a larger omission than it was on the arithmetic. It is also weighted by the
   **arithmetic** netlist's cell mix, not this one's, which is the precondition for adding the two
   ledgers and costs 2.1%: 0.118842 fJ per transition against 0.121346 on this netlist's own mix,
   so the 0.4512 pJ/MAC published here would be 0.4607 pJ/MAC re-weighted — the floor again, by a
   little. *(`ledger-scope.json` → `internal_mix_sensitivity`; `METHOD.md` § The flow, item 5.)*
5. **Everything is charged to one lane.** TENA and the TMP file are instantiated once for all eight
   lanes and the table charges them in full, which over-charges this lane by 0.0062 pJ/MAC
   (`gap.transport_charged_per_lane_mac_pJ` = 1.0266 against 1.0329). The **clock root** is the
   same question at 36× the size — 0.2231 pJ/MAC of a one-lane netlist's tree — and it is not
   divided, because an eight-lane netlist's root is not eight times this one's. Both sit inside the
   range §6 gives, and neither is divided in any published figure.
6. 🛑 **and one that points the other way: two of the eight parts are models**, the big one is an
   upper bound (§1), and the card's own `zeros` measurement says that upper bound is **too high**
   (§2). The floor and the ceiling are not on the same side of this ledger, which is why §6 gives a
   range — and why the range's own floor is not a floor on the truth.

---

## What was registered, and what happened

Nothing was pre-registered: this is a desk-compute pass on an open netlist with no card launch, so
there is no prediction to score. Three things did not go to plan and are named:

- **the `lq` Hamming ladder is not monotone on this netlist** (§3), so its designed-bit slope is
  reported with a 57% standard error rather than quoted as a result. The bus-bit regressor is;
- **both controls turned out to be composites** (§4). `+accfix` holds the index still and thereby
  also stops the accumulator word the index selects from changing; `+resfix` holds the result still
  and thereby also stops the read-back. Both are reported as composites against board numbers that
  are composites of the same kind, and the decomposition of the index term is given as a bound;
- **the per-lane control pipeline reads 0.0000 pJ** because `q129_lane_ctl`'s outputs are top-level
  nets of the scope design, so its switching is counted in the "top-level nets" row. The two rows
  should be read together; the split between them is a hierarchy artefact, not a result.

**Amended the same day, after an adversarial verification of this directory.** The verification
re-derived every published number from the committed JSONs — the per-part table to the last digit,
the census, the ladder rungs and slopes, both controls, the cap coverage, the board constants
against their sources, and `versions.txt` against the arithmetic run — and found no arithmetic
error. What it found were seven readings of those numbers, five of which moved one:

| # | what was published | what this file now says |
| --- | --- | --- |
| 1 | the 0.654 pJ floor is "the register files' clock gates and the clock root"; range 0.54–1.48 pJ (43–59% of the board) | 34% clock, 66% signal (the index sweep, which the card also performs); range **1.26–1.48 pJ (55–59% of the board)** |
| 2 | the register-file model is "a ceiling, bounded from below only by zero" | the card's own `zeros` figure (0.27 pJ/MAC, whole board) puts the model **above what the board permits**; "the result path closes" withdrawn |
| 3 | the index alone is 72–136 fJ, so "most of the composite is the data the index selects" | **166–175 fJ, 66–69% of the composite** — the counted bits had been priced at a per-*designed*-flip slope |
| 4 | §3's per-bus-bit sum, on the scope bench's counter, with `randn` as the cross-check | both denominators given; the two benches diverge 0.74×–1.40× per rung, worth 7 points of `lb` closure |
| 5 | the data-dependent `+internal` figure scaled by the whole-design ratio, 0.544 pJ | differenced, **0.518 pJ** |
| 6 | TENC's 0.0000 pJ "measured, not argued" | the bench ties TENC's five ports to zero (`tb_scope.sv` ll. 49–52), so the zero follows the stimulus; what is measured is its 0.0003 pJ clocked cost |
| 7 | §1 published 3.430 pJ and 59% / 79% unqualified | §1 carries the range |

The per-part table, the census, the ladder rung energies, both controls and the tool-version
identity with the arithmetic run are unchanged. `ledger_scope.py` carries the four code-level fixes
(marked `AMENDED`) and `ledger-scope.json` was regenerated from the same committed power JSONs; the
power JSONs, the SAIFs behind them and the census were **not** re-run, and nothing here needed a
card.

Tool versions are **identical** to the arithmetic's published run (`versions.txt` here against
[`../2026-10-26-open-netlist/versions.txt`](../2026-10-26-open-netlist/versions.txt)) — same yosys,
slang, Verilator 5.053, OpenROAD, ORFS, ASAP7 and core-et shas. Only the host differs (aifoundry1,
not aifoundry2), which is why the two ledgers can be added at all.

## Files

| File | What |
| --- | --- |
| `ledger-scope.json` | everything: the per-part table, the ladder fits with their standard errors, both controls with their composition, the census join, and the gap arithmetic in both readings |
| `power-mixed/power_gr_<pattern>.json` | the 15 runs on the `mixed` netlist: totals, coverage in nets and farads, the internal estimate, every block at three levels of hierarchy |
| `power-mixed-clkwide/` | `randn`, `zeros`, `ones` re-priced with a clock regex widened to catch the latch arrays' own gated branches (`clk_rf_wr[i]`, `clk_wr_data_a_n`, `enclk`). **The total is identical**; it is here to show that the clock/data split in the per-part table does not turn on the regex |
| `census_mixed.json` | the comparator census: flattened except the eight scope blocks |
| `census_keep.json` | the same with every boundary kept — its per-block counts carry the hierarchy penalty Q126(e) trap 5 describes |
| `sim_acct.txt` | the bench's own counters for all 15 runs: cycles, micro-ops, operand-bus bits, index bits, result bits, accumulator-read bits |
| `net_cap_globalroute_mixed.txt.gz` | wire and pin capacitance, in farads, for all 22,759 extracted nets |
| `stat_mixed.txt`, `stat_keep.txt` | Yosys's own cell report for each netlist |
| `versions.txt` | every tool and source sha |
| [`METHOD.md`](METHOD.md) | the scope read out of the RTL module by module, the two models and their bias, the flow's inherited blockers, the stimulus and the two controls |

Code: [`tools/open-flow/scope/`](../../../../tools/open-flow/scope/README.md) —
`q129_scope_top.v`, `tb_scope.sv`, `synth.sh`, `pnr.tcl`, `gatesim.sh`, `reduce.sh`,
`ledger_scope.py`, `asap7_seq_behav_scope.v`.
