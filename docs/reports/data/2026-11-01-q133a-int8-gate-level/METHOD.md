# Q133(a): how the gate-level counts were made

*The method behind [README.md](README.md). Sun 1 Nov 2026 (week 44), desk work on the Intel.*

## 1. The netlists

**The int8 unit.** `tima_top` and `tima_adder` from core-et `b38a1a31`, elaborated with yosys-slang and mapped onto ASAP7 RVT, TT corner,
by [`tools/open-flow/tima/synth_tima.sh`](../../../../tools/open-flow/tima/synth_tima.sh) with the open flow's own recipe
([`tools/open-flow/txfma/synth.sh`](../../../../tools/open-flow/txfma/synth.sh)): the same five liberty files, the same dont-use list, abc
at 1,250 ps, tie cells, flattened. The RTL leaves the multiplier's structure to the tool (`$signed(a) * $signed(b)` at `tima_top.v:89`, `+` at
`:94` and in `tima_adder.v:17`), so there is one netlist per architecture Yosys offers:

| arm | Yosys | the multiplier | cells | area (µm²) | nets | of which multiplier stage |
|---|---|---|---:|---:|---:|---:|
| `plain` | `synth -flatten` (txfma/synth.sh exactly) | the default `$mul`/`$macc` mapping: partial products summed in adders | 2,414 | 306.0 | 2,516 | 2,033 |
| `booth` | `synth -flatten -booth` | radix-4 Booth on B; the sums as alumacc leaves them | 1,999 | 252.2 | 2,101 | 1,618 |
| **`booth_tree`** (primary) | `synth -flatten -booth -arith_tree` | radix-4 Booth on B; the sums as carry-save trees | 2,019 | 253.6 | 2,121 | 1,636 |
| `booth_swap` | `booth_tree` on a copy of `tima_top.v` reading `in2 * in1` | radix-4 Booth on **A** | 2,016 | 253.5 | 2,118 | 1,634 |

(`netlists/stat_*.txt`, `netlists/stages_*.json`.) Every netlist has **92 flip-flops, the RTL's 92 register bits**: 32 + 4 for A (the
operand and its four sign bits), the same for B, 19 for the product sum and 1 for C's zap. **Which operand Booth recodes** is fixed by the
tool, not the RTL: yosys's booth pass recodes the second operand of `x * y`, checked on a 9×9 signed multiply alone in both orders
([`netlists/recoded_operand.txt`](netlists/recoded_operand.txt), `booth_operand.py`). As the RTL is written that is B, from TenB
(`vpu_lane_tima.v`: `f1_in1` = `tena_rd_data`, `f1_in2` = `tenb_out`).

**The primary arm is `booth_tree`**, the float unit's own kind of multiplier (radix-4 Booth and carry-save trees ending in one
carry-propagate add, which core-et writes out structurally for `txfma_top`), and what a datapath synthesis does with a sum of products. It
was chosen when the arms were built, and it was built and run first, but the choice was not registered: no timestamped record shows it came
before any count was set beside a card (corrected after verification; this read "named before any count was set beside a card"). `plain` is the open flow's recipe unchanged; `booth_swap` asks which operand the recoder sits on.

**The float unit**, for a like-for-like comparison: `txfma_top` as txfma/synth.sh's `flat` netlist and nothing else
([`synth_txfma_flat.sh`](../../../../tools/open-flow/tima/synth_txfma_flat.sh)): 16,063 cells, 2,127.4 µm², 1,953 flip-flops, 13 latches
(`netlists/stat_txfma_flat.txt`). The published Linux run of the same Yosys sha has 16,087 cells and 2,124.9 µm², with the same flip-flops and
latches: **abc maps 0.15% of cells differently on this platform's build**, so every netlist here can differ from a Linux run by about that.

## 2. One name per net, and a stage for each

[`netlist_stages.py`](../../../../tools/open-flow/tima/netlist_stages.py) rewrites each netlist without changing a cell or a connection
(`netlists/sha256.txt` pins both versions):

- every alias (`assign`, a vector and its part-selects) resolves to one scalar name; the ports keep their names and widths;
- each internal net is named for its stage, found from the netlist's own cones, in the RTL bench's convention for this unit
  (`settle_count.cpp` `stage_of()`, the `.lane_tima.tima.` branch): `f2_in_*` operand (the A and B words into the F2 registers, the enable
  multiplexers, the sign logic, the registers' outputs); `f2_prod_*` multiplier (everything between the F2 registers and the F3 product
  register, and its outputs); `f3_add_*` adder (after it: C's zap gates, the sign extension, the 32-bit add); `ctl_*` the enables' own logic;
  the output port `f3_out` is "result";
- every wire is declared public, so the simulator keeps each net as its own variable and a VCD gives each its own identifier.

**One difference of labels from the RTL count:** the RTL's output wire carries the adder's names as well as `f3_out`, so the RTL counter
credits it to the adder; in the netlist the adder's last cells drive the port directly, so those nets are "result". Compare the netlist's
adder plus result with the RTL's adder.

The float netlist gets the same treatment with `--generic`: no stage split, and the 13 gated-clock nets (combinational from the clock port
to a flip-flop's clock pin) named `clk_n*`, so the counter drops them exactly as it drops the RTL's clock-named signals.

## 3. Cells

[`liberty_models.py`](../../../../tools/open-flow/tima/liberty_models.py) writes each ASAP7 cell from the liberty file's own `function`,
`ff` and `latch` groups: one continuous assignment per output, a flip-flop as `always @(posedge CLK)`, a latch as `always @*`, and Verilator's
tracing off inside the file. So a VCD holds the netlist's nets and nothing of the cells' own; ASAP7's own models carry internal wires and
sequential UDPs the simulator refuses.

## 4. The bench, the counter, the check

[`rtl-sim/tima_gate`](../../../../rtl-sim/tima_gate/) is Q132(b)'s [`rtl-sim/fma_toggle_v2`](../../../../rtl-sim/fma_toggle_v2/) whole:
core-et's `vpu_top`, its micro-op stream, zero gate, clock gates and register files, with the netlist listed before the RTL so it is the
`tima_top` (16 per VPU) or the `txfma_top` (8 per VPU) that elaborates. Verilator 5.052 (conda-forge) with `-fno-dfg`. The counting is that
bench's, unchanged: `run_kinds.py` puts each tile through a coverage run behind the functional check (every accumulator word against
`accum.c`'s software after each measured op) and a VCD run of one whole op, which `settle_count` reads; **`nets_hier`** is one count per
net per cycle, a name merged only with the same waveform in an ancestor scope, over `.lane_tima.tima.` (int8) or `.txfma.` (floats) for the
unit and `.dut.` for the whole VPU. **`nets_map`**, Q132(b)'s primary since its §4, applies one list of merges learned once
(`train_maps.py`) to every run, so a regular stream cannot fold a fan-out that switches in step; `nets_hier` can, and reads low there. Per TensorFMA op on one minion; per MAC divides by 16,384 (int8), 8,192 (fp16) or 4,096 (fp32).

**The unit's registers stop reporting to the register accounting** in a gate run (they are flip-flop cells, not the `FF` macros), so the
clocked-bit term of every fit takes them from Q132(b)'s RTL run of the same tile: the same 92 bits a unit, the same stimulus.

**The control.** Q132(b)'s bench rebuilt here, unchanged, on four kinds at three launch points and four single-bit tiles, against its
committed counts point for point (README result 2).

## 5. What ran

| binary | tiles | launch points | maps |
|---|---|---|---|
| `booth_tree` | the 16 int8 kinds; E79's A list (`a8q`, `a8_0`…`a8_7`), E102's B list (`hq`, `bk_0`…`bk_7`) and its five masks | kinds: the three; single bits: the middle | `train_maps.py`'s |
| RTL (control) | `full`, `ones`, `zeros`, `gauss_q`; `hq`, `bk_5`, `a8q`, `a8_7` | kinds: the three; single bits: the middle | one stream |
| `plain`, `booth_swap`, `booth` | the 16 kinds; the A and B lists | the middle | one stream |
| float netlist | all 35 fp32 and fp16 kinds of `tools/claims-v3/kinds` (E78's 33 and the two zeros), in three batches; E102's all-in B lists, fp32 at bits 0, 11, 16, 22 and fp16 at 0, 9, with their zero tiles | the middle | one stream (fp32 `randn`) |

The middle launch point is 471,698 ops into a 0.5 s launch in int8 and 274,725 in the floats. "One stream" maps exist because `run_kinds.py`
needs a map for each binary. **Which merge is quoted where** (corrected after verification; this said no `nets_map` was quoted):

- kinds and fits are `nets_hier`, which uses no map, the convention the brief asked for;
- single bits are `nets_map` (README, Departures): `booth_tree`'s map is `train_maps.py`'s, and the others' are one-stream maps, quoted with
  that caveat;
- every RTL-side number also appears in Q132(b)'s primary, `nets_map`, read from Q132(b)'s committed counts, which its trained map made
  (`analysis.json` `merges`). The RTL control's own one-stream `nets_map` is never used.
