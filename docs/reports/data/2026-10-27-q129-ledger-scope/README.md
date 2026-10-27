# What the board pays besides the arithmetic — the lane's register files, operand bus and result path (Q129)

27 October 2026, on aifoundry1 (desk compute only; **no card was used**). The flow and how to
re-run it: [`tools/open-flow/scope/`](../../../../tools/open-flow/scope/README.md). The method, the
two models and the things that bound the answer: [`METHOD.md`](METHOD.md).

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
| **the transport, + the cells' internal energy** | **1.484** |
| **the two together** | **3.430** |
| E38/E39 at the board, over idle, three-card mean | **5.783** |
| the same at the minion rail (×0.750, E60's measured ratio) | 4.337 |
| **closure, was (arithmetic alone)** | **34% of the board, 45% of the rail** |
| **closure, now** | **59% of the board, 79% of the rail** |

And it is not a correction term in silicon either — on the same library and flow, one lane's
transport is **larger than one lane's arithmetic**:

| | cells | transistors | area µm² | flip-flops | latches | clock-pin cap fF |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| the arithmetic, `txfma_top` (`census_mixed.json` of Q126(e)) | 15,805 | 159,896 | 2,126.1 | 1,974 | 13 | 945.0 |
| **the transport, this netlist** | **21,608** | **200,504** | **2,532.4** | **340** | **3,540** | **1,844.0** |
| ratio | 1.37× | 1.25× | 1.19× | 0.17× | 272× | 1.95× |

🛑 **Most of that size is one of the two models, and it is an upper bound.** The 64 × 32 3-read
2-write VPU register file is a compiled macro the open library cannot build; it is replaced by
core-et's own **latch array** (`rf_latch_3r_2w`) at the same geometry, which is 15,685 cells and
1,718 µm² for 2 kbit — roughly an order of magnitude more area than a compiled macro would take.
Read the model rows as a **ceiling** on what the register files can account for, where the rest of
this ledger is a floor. [`METHOD.md`](METHOD.md) § "The two models, and which way they are wrong".

### 2. Per part

Switching energy per random multiply-add, one lane, ASAP7 RVT TT, 0.517 V, from
`power-mixed/power_gr_randn.json`. "data-dependent" is `randn` − `zeros`: what the part costs
because the operands move, as against what it costs for being clocked at all. `M` marks a model.

| part | pJ / MAC | data-dep. | clocked floor | + internal est. | signal toggles / MAC | cells | seq. bits | M |
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

Four things fall out, and the first is the one that matters:

- **the accumulator's register file is the single biggest item in the transport, 0.48 pJ per
  multiply-add on this model — 47% of the transport and a third of the whole new ledger.** It
  reaches that on 2,673 signal toggles per multiply-add, nearly as many as the arithmetic's whole
  3,299, because a 64-entry 3-port read path is a 64:1 mux tree per bit per port and the
  accumulator's index moves every cycle. **This is the model, so it is a ceiling**; a compiled
  macro reads through bitlines and would cost less. Nothing in this project has measured that
  number, and until something does, "the register file's read ports" is bounded between 0 and
  0.48 pJ per multiply-add, not estimated;
- **the operand bus and the result path cost 0.135 pJ per multiply-add**, and that figure is an
  **open-netlist result, not a model**: `vpu_bypass` is the real core-et module, 2,306 ASAP7 cells
  and 190 flip-flops, and all three source muxes and the five pipeline stages are in it;
- **the int8 accumulator file costs nothing on an fp32 multiply-add — 0.0000 pJ data-dependent,
  measured, not argued.** `vpu_tensorc_rf` has 1,344 cells and 562 latch bits sitting in every lane
  and an fp32 TensorFMA32 never reads or writes it. The RTL says so (every port
  `vpu_tensorfma.v` gives it is TIMA-prefixed) and this is the measurement;
- **the transport's clocked floor is 0.654 pJ, 63% of its switching energy.** That is what the
  register files' own clock gates and the clock root cost with every operand word zero. On the
  model's arithmetic that floor is dominated by the latch array's 64 per-entry clock gates, so it
  is the most inflated number in the table.

### 3. One flipped operand bit: 42% → 49% of the board, against 28% → 30% before

The same Hamming-ladder operand files E60 ran on three cards, fitted the way E60's own reducer fits
them — a line over h ≥ 1 against the *designed* flip count, free intercept. The arithmetic's slopes
are Q126(e)'s; the transport's are this netlist's; the board column is E60's **aifoundry3** block
(600 MHz, 521.8 mV, 4 passes).

| | arithmetic | **+ transport** | = sum | E60 at the board | at the rail (×0.75) | closure vs board | **vs rail** |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `lq` (quiet partner A = 1.0), switching | 32.9 | **16.4 ± 9.3** | **49.3** | 116.7 ± 0.6 | 87.6 | 42% *(was 28%)* | **56%** |
| `lq`, + the cells' internal | 46.3 | 21.0 ± 11.9 | 67.3 | 116.7 | 87.6 | **58%** | **77%** |
| `lb` (busy partner A = π), switching | 38.5 | **25.4 ± 6.4** | **63.9** | 129.9 ± 0.5 | 97.4 | 49% *(was 30%)* | **66%** |
| `lb`, + the cells' internal | 54.9 | 32.2 ± 7.8 | 87.1 | 129.9 | 97.4 | **67%** | **89%** |

Per **counted operand-bus bit** (E60's amendment-A2 regressor), where the fit is much better
resolved: transport `lq` **10.9 ± 2.7 fJ** and `lb` **12.1 ± 1.1 fJ**, on the arithmetic's 20.0 and
27.5, against E60's 74.7 and 85.6 fJ at the board — 41% and 46%.

🛑 **The `lq` designed-bit slope is not resolved, and the ladder is not monotone on this netlist.**
`lq` runs 0.734, 0.760, 0.867, **0.848** pJ at h = 1, 2, 4, 8: h = 8 is *below* h = 4, so the
standard error of the slope (9.3 fJ on 16.4) is 57% of it. `lb` is monotone except at h = 4 (0.739,
0.802, **0.787**, 0.934) and reads 25.4 ± 6.4. The transport's per-bit price depends on *which* bits
move, not just how many — a B-mantissa bit enters through TENB's 4-entry read and one mux, while the
accumulator's bits come through the 64-entry array — so a Hamming count is the wrong regressor for
it. The bus-bit column above is the one to quote, and the designed-bit column is carried only
because that is the column E60 published.

### 4. The result bit, and the register index: the two E60/E61 numbers that have a counterpart now

Both are differences against a control that holds one field still, "everything else the same"
(`+resfix`, `+accfix`). **Both are composites**, and that is the point: the control cannot move one
field in isolation, and neither could E60's or E61's card design.

| | bottom-up, transport | what the difference contains | board | at the rail | closure vs rail |
| --- | ---: | --- | ---: | ---: | ---: |
| **a result bit** | **23.58 fJ** (31.46 with internal) | 13.80 result bits/MAC through the F8 mux, the register-file write, **and the accumulator read-back they cause** | E60 **31.17 ± 0.17 fJ** (`xnz`) | 23.4 fJ | **101%** |
| **a changed read index** | **252.4 fJ** (440.2 with internal) | 1.94 index bits/MAC **and the 13.75 accumulator-word bits the new index selects** | E61 **369–452 fJ** | 277–339 fJ | **74–91%** |

- **The result path closes.** 23.58 fJ per result bit bottom-up against 23.4 fJ at the minion rail
  is 101% — the first **energy** rung in this project's chain to meet a card measurement rather than
  fall short of it. Read it with its ceiling warning: 0.48 pJ/MAC of the netlist it is measured on
  is the register-file **model**, and the result bit's path runs through that model's write port.
  One rung meeting its measurement after every other has fallen short is also the kind of result
  that is worth re-running before it is leaned on.
  It is also the composite above, not the write side alone: this design cannot separate the result
  word from the accumulator read-back it causes one pass later.
- **The register index does not close, and E61 said it would not.** E61 scored its own
  register-index ladder **under-resolved — "369–452 fJ per index bit, 12–14 times the page's 32 fJ,
  with no linear law across the three matched-rate rungs"**. The bottom-up composite is 252 fJ per
  index bit, 74–91% of E61's figure at the rail, which says the card number is the right order and
  that most of it is the *data* the index selects, not the index wires. Subtracting the
  accumulator-read bits at the transport's own fitted operand-bit slope leaves **72–136 fJ per index
  bit** for the index alone — a bound, not a measurement, because an accumulator bit and a B bit do
  not take the same path.

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
| **lower reading** — its data-dependent part only, + internal | **0.544** | **14.2%** | **22.8%** |
| of which **open netlist, no model at all**: `vpu_bypass` + `vpu_rf`'s own bypass + TENA/TENB/TMP, + internal | **0.290** | **7.6%** | **12.1%** |
| the same, data-dependent part only | 0.144 | 3.7% | 6.0% |
| TIMA accumulator file, on the fp32 path | 0.000 | 0% | 0% |

**The honest answer is the range, and the two readings differ by a factor of 2.7.** The upper one
charges the card for the whole netlist. The lower one charges it only for the part that moves with
the data, because the transport's 0.654 pJ clocked floor may already sit inside the **idle that E38
subtracts** — the same trap [`../2026-10-27-transistor-ledger/README.md`](../2026-10-27-transistor-ledger/README.md)
flags for the `zeros` pattern (*"the open flow's figure is the ungated root of this lane's clock
tree, which on a card is already inside the idle the measurement subtracts. 🛑 Do not quote it as
closure"*). Which it is depends on whether the lane's register files are clock-gated at idle on
silicon, which nothing here measures.

So in Q128's words: **the ledger moves from 1.946 pJ to between 2.49 and 3.43 pJ, and the closure
from 34% to between 43% and 59% of the board** (45% → 56–79% of the rail). The unaccounted 3.837 pJ
falls to between 3.29 and 2.35 pJ.

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
   here — is a larger omission than it was on the arithmetic.
5. 🛑 **and one that points the other way: two of the eight parts are models**, and the big one is
   an upper bound (§1). The floor and the ceiling are not on the same side of this ledger, which is
   why §6 gives a range and not a number.

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
