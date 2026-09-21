# fma_toggle: how many nets flip in the multiply-add unit, per data pattern

The ET-SoC-1 draws 38 W multiplying matrices of zeros and 66 W multiplying random ones, at the same speed
(docs/reports: horace-experiment). This bench asks the RTL why. It drives eight copies of core-et's
`txfma_top` (the 7-stage fused multiply-add unit, one per vector lane) with the exact micro-op stream of a
16x16x16 `TensorFMA32` and counts what switches.

What is modelled, from the RTL:

- **Order of operations** (PRM 9.4, `vpu_tensorfma.v`): for each B row k, for each A row i, two micro-ops
  (C columns 0-7, then 8-15), each `c = a*b + c` on 8 lanes. One micro-op per cycle, 512 per op, then a
  34-cycle gap (the card measures 546 cycles per op for every data pattern).
- **Zero gating** (`vpu_ctrl.v`, `ex_fma_gate_mask`): on an accumulate pass a lane gets no valid when its A
  or B operand word is zero. The unit's pipeline registers are enabled by the valid bit of their stage, so a
  gated lane clocks nothing and flips nothing. The first op of a launch is a multiply pass and is not gated.
- **Clock gate** (`vpu_lane.v`): the unit's clock runs while micro-ops arrive and for 7 cycles after.
- Results return to the C registers after 7 cycles, as in the chip, so later micro-ops see real accumulator
  values. Every result is checked against software (`+check`): 8,192 of 8,192 match for random data.

What is counted, per op and per minion:

| Counter | Meaning |
| --- | --- |
| `nets` | Toggles of every named net and register bit inside the eight units (Verilator toggle coverage, both edges, clocks excluded) |
| `by_block` | The same, by RTL file: the Booth/Wallace multiplier tree, the adder, the shifters, ... |
| `ff_clocked` | Register bits that received a clock edge with their enable high (`ff_acct.sv` replaces `libs/registers`) |
| `ff_toggles` | Register bits that changed |
| `bus` | Toggles of the operand words presented to the lanes (activity outside the unit: register-file reads, bypass) |
| `lane_valid` | Lane-cycles with a valid multiply-add, out of 4,096 |

Limits: RTL, not a netlist, so a "net" is a named signal (module ports are counted at each level of the
hierarchy); zero-delay simulation, so no glitches; the Erbium-branch RTL is the same core lineage as the
ET-SoC-1 but a later revision; only the multiply-add units are simulated, not the scratchpad, the register
file or the tensor state machine around them.

```
make CORE_ET=../../external/core-et          # builds obj_dir/Vtb with Verilator 5 (about 1 minute)
python3 tiles.py randn /tmp/t.hex --iters-before 1000
./obj_dir/Vtb +tiles=/tmp/t.hex +ops=4 +warm=1 +check=8    # ACCT {...} line, CHK lines, final C
python3 toggles.py --out toggles.json --tiles-dir <dir of tiles dumped by sparsity_host --dump-tiles>
```

`toggles.py` runs each pattern at four points of a launch (accumulators at 0, 1e3, 1e5 and 4e5 ops) and
averages the last three. Random data flips about 87 million counted nets per op, three quarters of them in
the multiplier's carry-save tree; a constant flips about 30 thousand; zeros flip none.
