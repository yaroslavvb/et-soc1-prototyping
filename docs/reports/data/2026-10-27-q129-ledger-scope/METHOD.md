# How the lane's transport was priced (Q129, scope)

Companion to [`README.md`](README.md), which has the results. This file is the method, the two
models and the things that bound the answer. The flow:
[`tools/open-flow/scope/`](../../../../tools/open-flow/scope/).

## What the unit under test is

[`tools/open-flow/scope/q129_scope_top.v`](../../../../tools/open-flow/scope/q129_scope_top.v)
is one VPU lane's **transport**: everything a FP32 TensorFMA32 multiply-add exercises on the way
to and from the arithmetic, and nothing of the arithmetic itself. Each part was found by reading
the public `core-et` RTL (branch `erbium`, sha `b38a1a31`, the revision
`tools/open-flow/txfma/setup.sh` pins) and following the micro-op from the register files to
`txfma_top` and back:

| part | core-et module | where it is instantiated | per lane? |
| --- | --- | --- | --- |
| operand **A** file, 32 b × `VPU_TENA_SIZE` = 2 | `vpu_tensora_rf` → `rf_latch_1r_1w` | `vpu_ctrl.v` l. 1806 | **no — one for all 8 lanes** |
| operand **B** files, 32 b × `VPU_TENB_SIZE/2` = 4, `VPU_NUM_TIMA` = 2 of them | `vpu_tensorb_rf` → `rf_latch_1r_1w` | `vpu_lane_tima.v` l. 42 | yes, ×2 |
| the **accumulator**: the VPU/FP register file, 64 × 32, 3 read 2 write | `vpu_rf` → `vpu_64x32_3r2w_vpurf` | `vpu_lane.v` l. 283 | yes |
| the **operand bus** and the **result path**: three 32-bit 13-way source muxes, the F4…F8 `vpu_output_t` pipeline with per-stage clock enables, the F8 result mux | `vpu_bypass` | `vpu_lane.v` l. 318 | yes |
| the **TMP** file, 32 b × 8 | `vpu_tensortmp_rf` → `rf_latch_1r_1w` | `vpu_ctrl.v` l. 1832 | **no — one for all 8 lanes** |
| the **TIMA accumulator** file, 32 b × 16 | `vpu_tensorc_rf` → `vpu_tensorc_rf_buffer_array` | `vpu_lane_tima.v` l. 60 | yes, but **int8 only** |
| **per-lane control**: the {waddr, wmask, thread_id} pipeline F3…F8 and the lane's clock gates | inline in `vpu_lane.v` (l. 218–250, 335–365) | — | yes |

**TENC is not on the fp32 path.** Every port `vpu_tensorfma.v` gives it is TIMA-prefixed
(`f2_tima_tenc_raddr`, `f3_tima_tenc_wen`), and `vpu_tensorfma.v`'s own header says the FP32
instruction "accumulates the result in the FP registers (C matrix)" — the VPU register file. It is
built and priced here anyway, to find what carrying an unused block costs: 0.0003 pJ per
multiply-add for 1,344 cells and 562 latch bits in every lane.

🛑 **That is an RTL reading, and this bench does not independently confirm it.** `tb_scope.sv`
ll. 49–52 declare `tenc_wen = 0`, `tenc_ren = 0`, `tenc_waddr = 0`, `tenc_raddr = 0`,
`tenc_wdata = 0` and never assign them again — the ports appear nowhere else but the port map at
ll. 65–66. The bench ties TENC off *because* of the RTL reading, so the 0.0000 pJ data-dependent
figure is a property of the stimulus, not evidence for the reading. An independent check would
drive TENC's ports from the unit's own control on an fp32 stream and show they are never raised.
The amended README says this where it reports the number.

## The two models, and which way they are wrong

Two blocks are **compiled macros**: the RTL instantiates a module the public tree does not
contain, so the open library cannot build them. Each is replaced by **core-et's own latch-array
register file from `rtl/libs/rf_latches`, at the same geometry**:

| macro | model | geometry |
| --- | --- | --- |
| `vpu_64x32_3r2w_vpurf` | `rf_latch_3r_2w #(.WIDTH(32), .ENTRIES(64), .LEVEL2_CLK_GATE(1))` | 64 × 32, 3 r, 2 w |
| `vpu_tensorc_rf_buffer_array` | `rf_latch_1r_1w #(.WIDTH(32), .ENTRIES(16), .LEVEL2_CLK_GATE(1))` | 16 × 32, 1 r, 1 w |

`vpu_rf.v`'s read/write collision bypass is kept **verbatim** around the model, so only the array
is substituted. A third model, `q129_lane_ctl`, stands in for the per-lane half of the control
that `vpu_ctrl.v` shares across the eight lanes: the index/mask/thread pipeline at exactly
`vpu_lane.v`'s widths, built from core-et's own `` `FF `` macros and `et_clk_gate`, plus the
`TXFMA_CLOCK_EN_DELAY` = 7 clock-valid chain. The logic that *computes* those indices upstream is
not in it.

🛑 **A standard-cell latch array is an upper bound on a compiled register-file macro, and the bias
is large.** A 2 kbit 3r2w macro at 7 nm is built from bitcells, bitlines and sense amplifiers; the
model is 2,243 ASAP7 latches behind 64 per-entry clock gates. Two consequences, both stated with
every number taken from it:

- its **clock capacitance is far larger** than a macro's would be — the model's array alone carries
  1,066 fF of the design's 1,844 fF of clock-pin capacitance, so any clock-tree share quoted from
  this netlist is a ceiling, not an estimate;
- its **area**, 1,718 µm² for 2 kbit, is roughly an order of magnitude above a compiled macro's,
  which is the clearest signal of the substitution's size.

So the two model blocks give a **ceiling** on what the register files can account for, where the
rest of this directory (like the arithmetic ledger before it) gives a **floor**. Both are useful
and neither is the answer; the README keeps the open-netlist rows and the model rows apart in
every table.

🛑 **And the card says the ceiling is above what the board permits.** E38 ran the same instruction
stream with zero operand data and the whole board cost **0.27 pJ per multiply-add over idle**
(three-card registered mean, Q128 `data.json` → `/permac/mean_zeros_pJ`; per card 0.1633 / 0.4034 /
0.2512). This netlist's `zeros` run is that stimulus, and one lane's transport costs 0.6540 pJ in
it — 2.42× the whole board, 1.60× it on the 0.4310 pJ signal part alone, and the register-file
array row **by itself** (0.3050 pJ, all of it signal) is 1.13× it. Either the lane's clocks run at
idle, in which case the card's figure excludes clock and the signal part is what has to fit inside
0.27 pJ, or they are gated, in which case the whole 0.6540 pJ does. Both ways the model
over-prices. That is a stronger statement than "a ceiling with nothing below it but zero", and it
is why the README withdraws the result-bit closure claim: the result bit's path runs through this
model's write port. `ledger_scope.py` computes the check (`gap.card_zeros_bound`).

**What the table charges to one lane.** TENA and the TMP file serve all eight lanes and the
per-part table charges them in full; dividing those two by `VPU_LANE_NUM` = 8 gives 1.0266 pJ/MAC
against 1.0329 (`gap.transport_charged_per_lane_mac_pJ`). The clock root — 0.2231 pJ/MAC — is the
same question at 36× the size and is **not** divided, because an eight-lane netlist's clock root is
not eight times a one-lane netlist's; it would have to be built to be known. Both are inside the
range the README's §6 gives, and the convention is stated in `gap.charging_convention`.

## The flow, and what it inherits from Q126(e)

Identical to the arithmetic's, so the two can be added: Yosys + yosys-slang onto **ASAP7 RVT, TT**
(a predictive 7 nm library, BSD-3-Clause, *not* the process the chip was built in), the ORFS
`asap7` platform at 1×, an SDC of 1250 ps, OpenROAD floorplan → place → `repair_design` → CTS →
global route → per-net capacitance, then the operand stream driven into the gate netlist under
Verilator with a SAIF, priced at **½CV² per toggle, CV² per clock cycle, at 0.517 V** — the
minion rail — by the same `tools/open-flow/txfma/power.py`.

Everything the arithmetic's `POWER.md` says about this flow holds here too, and nothing was fixed:

1. **detailed routing does not close**, so there is no SPEF and **no coupling capacitance**: the
   between-cell wire is a global-route Steiner estimate, a lower bound on every wire. Both scope
   netlists failed the same way as the arithmetic's (`drok=0`);
2. **half the capacitance is unpriced** — the nets CTS and `repair_design` made after the netlist
   was simulated. The coverage figure is in `ledger-scope.json` under `totals.cap_fraction_priced`;
3. **no glitch factor** (the timed pass's Icarus blocker is unchanged);
4. the SDC is missed, so the clock tree CTS built is the answer to a constraint the design does not
   meet, exactly as in `POWER.md`;
5. the cells' own internal energy is the same census-weighted estimate (0.1188 fJ per transition at
   0.517 V) over **combinational** transitions only — the 3,540 latches' and 340 flip-flops' own
   clock-pin internal energy is on top of it, and on a design this sequential that is not small.
   **The mix is the arithmetic netlist's, applied unchanged here**, and that is deliberate: it is
   the same per-transition constant on both sides of the addition, which is what lets the two
   ledgers add. It is **not** this netlist's own mix, although `power.py`'s `--cell-energies` help
   text says "this netlist's own cell mix" — the weights come from `census_weighted_mix` in
   `2026-10-26-asap7-cell-energies/asap7-cell-energies.json`, whose own `source` line names
   txfma_top flattened, and every `power-mixed/*.json` here therefore repeats the arithmetic
   netlist's census (`combinational_cells_priced: 14119`, `DFFHQx4: 1953`) rather than this one's
   (17,701 combinational; 3,143 `DHLx1` + 397 `DLLx1` latches; 340 `DFFHQx4`). **The cost of using
   the shared mix is 2.1%**, and it is in the conservative direction: re-weighted on this netlist's
   own cell mix the constant is 0.121346 fJ per transition against 0.118842, so the published
   0.4512 pJ/MAC would be 0.4607. `ledger_scope.py --cell-energies` computes this as a labelled
   sensitivity (`internal_mix_sensitivity`); the power JSONs are left as the tool produced them.
   19 cells of this netlist (4 combinational types, 10+5+2+2) have no liberty entry in the mix and
   are not priced at all.

## The stimulus

The **same operand files** the arithmetic ran on, written by
`tools/open-flow/txfma/mktiles.sh`: the 21 Sep `randn` / `ones` / `zeros` patterns at
`--seed 1 --iters-before 1000`, and V3-HL's Hamming-ladder rungs `lq_h{0,1,2,4,8}` and
`lb_h{0,1,2,4,8}` — the files E60 ran on three cards.

`tb_scope.sv` walks the same micro-op order as `tb_gate.sv` and `rtl-sim/fma_toggle/tb.sv`
(for each B row k, for each A row i, two micro-ops), and routes each operand the way the RTL routes
it: A written into TENA and read back out of it, B into TENB (`raddr[0]` picking which of the two
TIMA files, as `vpu_lane.v` l. 315 does), the accumulator living in the VPU register file at index
2 i + h — this lane's own 32 registers — read on every micro-op and written back at F8. The
arithmetic's answer is supplied at the design's `txfma_res_data` port, computed in the simulator's
own fp32 arithmetic.

**Two departures from the card, both stated:**

- the bench's fp32 multiply-add rounds the product before the add, where the unit fuses. The
  written-back words can differ from the silicon's in the mantissa's last place. 🛑 **The first
  version of this file called that "a fraction of one bit in 32" for a toggle count, and the
  evidence does not support it**: the accumulator is re-read and rewritten 512 times in a run, so a
  last-place difference compounds, and this bench's `bus_toggles` for the *same operand files*
  differ from the arithmetic bench's by far more than one bit in 32 —

  | rung | this bench | the arithmetic bench | ratio |
  | --- | ---: | ---: | ---: |
  | `lq_h1` | 1,142 | 1,123 | 1.02 |
  | `lq_h2` | 2,168 | 2,147 | 1.01 |
  | `lq_h4` | 5,754 | 4,617 | **1.25** |
  | `lq_h8` | 7,272 | 6,959 | 1.04 |
  | `lb_h1` | 1,160 | 1,565 | **0.74** |
  | `lb_h2` | 3,200 | 2,532 | **1.26** |
  | `lb_h4` | 3,710 | 3,891 | 0.95 |
  | `lb_h8` | 9,318 | 6,666 | **1.40** |
  | `ones` | 68 | 31 | **2.19** |
  | `randn` | 17,394 | 17,349 | 1.00 |

  The rounding departure is one contributor and the two benches' bus definitions are another (this
  one counts at `vpu_bypass`'s operand ports, the arithmetic's at `txfma_top`'s `in1/in2/in3`);
  nothing here separates them. `randn` — the pattern the first version quoted as its cross-check —
  is the one rung where they agree, which is what a 0.3% agreement on a 17,000-toggle pattern will
  look like whether or not the counters match on the sparse ones. The consequence is in the
  README's §3: the transport's per-bus-bit slope is published on **both** denominators, and only
  the fit against the arithmetic bench's own counts may be added to the arithmetic's 20.0 / 27.5 fJ
  (`ledger_scope.py --acct-arith`, `ladder.<fam>.bus_arith`);
- `q129_lane_ctl`'s EX→F8 distance is 6 cycles against the lane's 8. The operand and result **bit
  patterns** are the stream's either way, and the accumulator is re-read 32 micro-ops after it is
  written, so the dependency is satisfied at either latency.

## Two controls, so a term can be had by difference

Both are "everything else the same", on the pattern of E60's and E61's own designs:

| control | what it holds still | what the difference gives |
| --- | --- | --- |
| `+accfix=1` | the accumulator's register **index**, at 0 instead of sweeping 2 i + h | the bottom-up counterpart of E61's 369–452 fJ per changed read-index bit |
| `+resfix=1` | the **word** the arithmetic hands back at F8 | the result path's own data-dependent energy, against E60's 31.2 fJ per result bit |

Each run is also taken as a difference of two simulations of the same bench — one with the measured
ops and one with none (`_o1` against `_o0`) — because a SAIF counts the whole simulation.
