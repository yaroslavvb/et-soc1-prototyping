# fma_toggle_v2: the real vector unit, returning correct multiply-adds

`rtl-sim/fma_toggle` and `rtl-sim/fma_toggle_formats` drove `txfma_top` and `tima_top` from a testbench that coded the micro-op stream, the
zero gate and the write-back itself, and their multiply-add returned wrong values. They stay as the record. This bench replaces them for any
count that is quoted. Results and the reasoning: [`docs/reports/data/2026-11-01-q132-rtl-bench/README.md`](../../docs/reports/data/2026-11-01-q132-rtl-bench/README.md).

## Why the old benches returned wrong values

**Not the stimulus: the simulator.** Verilator 5.052's data-flow-graph optimiser miscompiles core-et's `casez` blocks that have a wildcard arm
and part-select targets. One of them is the mux in front of the alignment shifter (`txfma_f3.v:160-170`). With the pass on, that mux reads 0, so
nothing reaches the adder but the larger operand, and a multiply-add returns c alone, or a·b alone when c is 0. **`-fno-dfg` is the fix**, in
this Makefile's `VOPT`. [`verilator_dfg_reproducer.sv`](verilator_dfg_reproducer.sv) shows it in 25 lines of code with no RTL from this project: `al=0000`
with the pass, `al=4000` without. [`tb_prev.sv`](tb_prev.sv) shows that `use_prev_sigs` has nothing to do with it: the result is wrong with the
flag on and off when the pass is on, and right with the flag on and off when it is off.

The other faults were real testbench faults, and they are gone because the testbench no longer does those jobs:

| Fault in the old benches | What it did | Now |
|---|---|---|
| `uop_prev` set after any valid (`fma_toggle/tb.sv:94`) | a lane whose first MADD micro-op was gated keeps the MUL control word (`txfma_c0.v:222`) and returns a·b: partly gated kinds only | `vpu_ctrl.v:849-861` sets the flag, only after a micro-op with all eight lanes valid |
| int8's C taken from the EX-stage word | `tima_top.v:111` adds C in F3, two cycles after a and b, and `vpu_lane_tima.v:60-71` reads TenC at F2 | the real `vpu_lane_tima` and TenC |
| the write-back mask read a cycle stale | gated kinds only | the real write-back |
| a first op that was all MUL | the RTL multiplies only in a launch's first A column (`vpu_tensorfma.v:726`) | the real FSM |

## What it is

[`tb_vpu.sv`](tb_vpu.sv) instantiates `vpu_top` whole: `vpu_ctrl`, `vpu_ml`, `vpu_tensorfma`, all eight `vpu_lane`s with their register files and bypass,
`txfma_top`, `tima_top`, TenA, TenB, TenC, TenTMP.

**What remains testbench code, and nothing else does:**

1. **The scratchpad.** An array that answers the VPU's read port two cycles later, always. It never refuses a bid. The dcache is not modelled.
2. **The core.** One `tensorfma_start` pulse with a control word in the bit layout of `workloads/sparsity/kernel/sparsity.c` `fma_word`, then idle. The gap
   before the next start stands for the core's loop.
3. **Back doors.** Writes of C into the RF or TenC memories, to start an op at a chosen point of a launch, and reads of them to check it.

One free-running clock. The chip's PLL, clock tree and wires are not modelled, and everything is zero delay, so no glitches.

**What the real state machine then shows by itself:** 538 cycles start to start in fp32 and fp16 and 310 in int8, where the card measures 546.001 and
318.000 (E78). Both differ by the same 8 cycles, the core's loop. 512 micro-ops of 8 lanes against 256 of 16 slots. All 51 kinds' valid slot counts equal
`kinds.json`'s `gated_lane_frac`.

## Build and check

```
make CORE_ET=../../external/core-et          # Verilator 5 on PATH; about 30 s on 10 cores
make check                                   # the functional check, about 1.5 min
python3 train_maps.py --bin obj_vpu/Vtb --settle ./settle_count --kinds ../../tools/claims-v3/kinds --out maps    # 20 s; a map belongs to its binary
python3 run_kinds.py --bin obj_vpu/Vtb --accum ./accum --settle ./settle_count --maps maps --kinds ../../tools/claims-v3/kinds --out counts.json --jobs 8   # 51 kinds, about 4 min on 10 cores
```

The mini's Verilator came from Homebrew (`brew install verilator`, 5.052). For a Mac with conda-forge's Verilator, see `../fma_toggle/README.md`.
`core-et` at `b38a1a31`. numpy is needed only by the analysis scripts in the data directory.

**No count may be quoted from a run that fails the check.** `run_kinds.py` compares every accumulator word with software after each measured op
and records `check_mismatch`. A pass tests arithmetic, order and the gate at the end of an op: it does not validate the toggle counts, and fp16's software
is a model read off this same RTL. See the data directory's Result 3.

## Files

| File | |
|---|---|
| `tb_vpu.sv` | the bench around `vpu_top` |
| `tb_unit.sv`, `fcheck_unit.py` | one `txfma_top` against an exact rational reference: random and corner operands, flush rules, near-cancelling sums |
| `fcheck_vpu.py` | whole TensorFMA ops in three formats against a software replay of the order and the gate, word by word, plus the gate's slot count |
| `fcheck_all.sh` | both, with a pass/fail exit |
| `fp16_model.py` | fp16's arithmetic as the RTL's fixed-point window computes it: it is not exact arithmetic |
| `accum.c` | the accumulators a launch has reached after n ops, in software (the same rules, ported), so an op can start mid-launch |
| `ff_acct.sv`, `macros_acct.vh`, `acct.cpp` | register accounting for **every** register, including the `FF` macro family the first recount could not see |
| `settle_count.cpp` | `../fma_toggle/settle_count.cpp` plus `hier2`, the learned merge map, and a stage for each merged net; its five original counts are computed as before |
| `train_maps.py` | learns once, on random data in every format, which RTL names are one net |
| `run_kinds.py` | every tile through coverage and a VCD, by stage, behind the check |
| `tb_flip.sv`, `flip_stages.py` | one flipped operand bit, diffed between two traced runs |
| `tb_prev.sv` | `use_prev_sigs` on and off, as a direct test |
| `verilator_dfg_reproducer.sv` | the simulator fault, reduced |
