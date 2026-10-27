# Place, route, parasitics and switching power of the open netlist (Q126)

26 October 2026, on aifoundry2. Companion to [`README.md`](README.md) (the cell census). The flow:
[`tools/open-flow/txfma/`](../../../../tools/open-flow/txfma/README.md), scripts `pnr.tcl`,
`gatesim.sh`, `tb_gate.sv`, `power.py`.

**What this answers.** The project's per-flip prices are all a measured watt divided by a toggle
count that came from one bench, and the one gate-level recount that exists was made with a
tape-out flow nobody outside can run. Here the same stimulus is driven into the open netlist, the
capacitances come from an open extractor and an open 7 nm library, and the energy is arithmetic
anyone can repeat.

## What ran, and what did not

| Step | State |
| --- | --- |
| Floorplan, pin placement, global placement, `repair_design`, detailed placement | done |
| Clock-tree synthesis (`BUFx2/3/4/5`), propagated clock | done, 257 clock nets |
| Global route, Steiner parasitics, per-net capacitance for all 20,383 nets | done |
| SDF written for the timed pass | done, 18 MB |
| **Detailed route (TritonRoute), OpenRCX, SPEF with coupling caps** | **blocked** |
| **The timed (SDF-annotated) pass, and so the glitch ratio** | **blocked** |

Both blockers are written up at the end. Everything below therefore uses the **global-route
Steiner estimate** of wire capacitance, not an extraction: it has no coupling term, so it is a
lower bound on the wire half of each net, while the pin half comes from ASAP7's liberty and is
exact.

## Toggles and energy per multiply-add

One lane, one TensorFMA32 op (512 micro-ops, 547 cycles), ASAP7 RVT TT, 1250 ps (800 MHz),
**0.517 V**, the minion rail. Energy is switching only: ½CV² per toggle, CV² per clock cycle.
Activity is the difference of two runs of the same bench, one with the measured op and one
without, because a SAIF counts the whole simulation.

| Pattern | flipped input bits / mul-add | signal toggles / mul-add | pJ / mul-add | clock's share |
| --- | ---: | ---: | ---: | ---: |
| `randn` (the 21 Sep random tile) | 33.9 | **3,623** | **1.516** | 32.7% |
| `lb_h8` (Hamming ladder, busy partner, h = 8) | 13.0 | 1,759 | 0.962 | 51.6% |
| `lb_h0` (the ladder's own zero rung) | 0.23 | 37 | 0.509 | 97.6% |
| `ones` | 0.06 | 31 | 0.507 | 97.9% |
| `zeros` | 0 | 0.008 | 0.217 | 100% |

Flipped input bits are the bench's own `bus_toggles` (the in1/in2/in3 words presented to the lane),
in `power/sim_acct.txt`.

Three things fall out:

- **Zero gating shuts 57% of the clock tree.** With every operand word zero the lane gets no valid
  bit, the unit's 13 clock gates stay shut, and the clock capacitance that still toggles falls from
  1,846 fF to 802 fF. Four signal toggles survive in the whole op. The 0.217 pJ per multiply-add
  that remains is the ungated root of the tree, and it is the floor this unit cannot go below while
  its clock runs.
- **The clock tree is a third of a busy multiply-add and nearly all of an idle one.** At `randn`
  it is 32.7% of the switching energy; at `ones`, where the data barely moves, 97.9%. Any model
  that prices a load by its flipped bits alone is pricing the smaller half at low activity.
- **Energy per flipped input bit, inside the multiply-add, is about 35 fJ.** From the ladder:
  (0.962 − 0.509) pJ over (13.02 − 0.23) flipped bits = **35.4 fJ per flipped operand bit**.
  E60 measured **116.7 fJ** at the board for the same kind of flip. So one lane's multiply-add
  switching is about **30%** of what the board pays, which leaves the register-file read ports, the
  operand bus, the cells' own internal energy and leakage — the project's picture that transport
  dominates, now with an independent number on the arithmetic half.

## Per block, random data

Toggles per multiply-add and the energy they cost, from `power/power_gr_randn.json`:

| Block | toggles / mul-add | pJ per op | fJ / mul-add |
| --- | ---: | ---: | ---: |
| Booth rows (`f1/ppg`) | 439.1 | 39.27 | 76.7 |
| Wallace tree (`f1/wallace1` + `f2/wallace2`) | 716.3 | 92.98 | 181.6 |
| Product adder (`f2/prod_adder_64b`) | 45.4 | 5.49 | 10.7 |
| **multiplier (the three together)** | **1,200.8** | **137.7** | **269.1** |
| normaliser (`f5/norm_shf`) | 226.6 | 24.77 | 48.4 |
| aligner (`f3/align_shf_48`) | 183.3 | 17.39 | 34.0 |
| leading-digit (`f4/lxd_ps_hi`) | 175.2 | 17.32 | 33.8 |
| exponent (`txfmaexp0_top`) | 46.3 | 8.90 | 17.4 |

**The multiplier's 1,200.8 physical toggles per random multiply-add stand against the tape-out
flow's 1,244 — 3.5% apart.** Two independent flows, two different 7 nm libraries, the same RTL and
the same stimulus. That is the first outside check this count has had, and every per-toggle price
in the project is a watt divided by a number like it.

For the other disputed count: the RTL bench counts 21,331 toggles of *named RTL signals* per random
multiply-add; Sunday's recount of the same RTL on the same stream gets 7,160–7,470. The open
netlist's whole unit, counted on real wires with each one paid for once, gives **3,623 signal
toggles** — below the recount, as it should be, because a physical wire carries several RTL names
(the as-built work puts it at 2.55 across the unit, 3.5 in the tree; 7,160 ÷ 2.55 = 2,808, same
order). The lab's 21,331 is not reproduced by either.

## Files

| File | What |
| --- | --- |
| `power/power_gr_<pattern>.json` | totals, coverage, and every block at three levels of hierarchy |
| `power/sim_acct.txt` | the bench's own counters per run (cycles, valid lane-cycles, flipped bus bits) |
| `net_cap_globalroute.txt.gz` | wire and pin capacitance, in farads, for all 20,383 extracted nets |

Coverage, for `randn`: 10,460 of the 20,383 extracted nets are found in the simulation and carry
activity or zero; 236 clock-tree nets are priced from the gated clock they branch off, because CTS
made them after the netlist was simulated. The 9,923 not found are nets the simulator folded away
or that the CTS/`repair_design` passes added; they are mostly buffer-to-buffer wires, and leaving
them out makes this an underestimate.

## The two blockers, and what would clear them

1. **Detailed routing does not close, so there is no SPEF and no coupling capacitance.**
   TritonRoute in the only OpenROAD binary available without root (the litex-hub conda build,
   `f12e2f47`, mid-2022) fails with `DRT-0255 Maze Route cannot find path` on a block pin, at
   utilisations of 40%, 30% and 22%, with pins on M4/M5 and with the routing range opened to M9.
   At 30% it had completed 20% of the first iteration with zero violations before the pin failed,
   so this is pin access, not congestion in the core. **What would clear it:** a current OpenROAD
   (the ORFS Docker image, or a source build — neither was available here: Docker is not running on
   the Intel and a source build needs root), or a `-exclude` region for the pins. With it,
   `pnr.tcl` already runs `extract_parasitics` and `write_spef` and re-reads the SPEF.
2. **No timed pass, so no glitch number.** Icarus is the only simulator here that can take the SDF,
   and it refuses two things: ASAP7's own sequential models (`sorry: ifnone with an edge-sensitive
   path is not supported`, `asap7sc7p5t_SEQ_RVT_TT_220101.v:83`) and core-et's
   `rtl/inc/shire_assert.vh:104` (a syntax error under `-g2012`). Verilator, which does compile
   both the netlist and the bench, has no delay model at all. **What would clear it:** strip the
   `specify` blocks from a copy of the ASAP7 SEQ models and give the bench a cut-down header
   without `shire_assert.vh`, or use any simulator with full SDF support. The SDF itself is
   written and waiting (`work/pnr/txfma.sdf`, 18 MB, post-CTS).

Until then the glitch ratio in the record — 1.5× the toggles and 1.4× the energy in the multiplier
tree — still rests on the tape-out flow alone.
