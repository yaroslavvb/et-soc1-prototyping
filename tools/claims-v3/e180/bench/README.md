# E180's bench: the energy catalogue's vector-add loop on core-et's whole minion, both harts

*Thu 5 / Fri 6 Nov 2026, Q146(f), lane `add-q146f`. Built and run on the mini (Verilator 5.052, Homebrew; the version
`rtl-sim/fma_toggle_v2` uses), through `run_remote --host mini`. Nothing here touched a card or a lab box.*

## What it is

[`tb_minion_e180.sv`](tb_minion_e180.sv) instantiates core-et's `minion_top` whole (`b38a1a3`, github.com/openhwfoundation/core-et,
`rtl/shire/minion/minion_top.v`): the front end (two thread buffers, the thread scheduler that alternates the harts, the RVC
expander, the VPU decoder), the integer pipe (decode, scoreboards, CSRs with their PMU-read replay), the dcache, and
`vpu_top` with all eight lanes, their register files, bypass and txfma. The program is the energy catalogue's inner loop
(`workloads/enercat/kernel/enercat.c` RUN() with `gen_ops.py`'s generated block), assembled by [`asm_e180.py`](asm_e180.py).

**What remains testbench code, and nothing else:**
1. The neighbourhood's shared instruction cache (`rtl/shire/neigh/neigh_shared_icache.v`, not instantiated): a request
   accepted in the minion's F1 is answered in its F5, four cycles later, always a hit; `+icq=k` grants a request only every
   k-th cycle (contention from the other minions; 1, the primary, is never contended).
2. The neighbourhood PMU's read path as `rtl/shire/neigh/neigh_pmu.v` writes it (the select flopped, then the counter
   flopped: two cycles); the counter is the bench's cycle count, so `csrr hpmcounter3` behaves as in the kernel's `cycles()`.
3. Ties: no data-cache traffic is made (the program needs none), PTW, interrupts, debug, DFT, APB and ESRs idle.
4. Read-only back doors: the RF words and each hart's `++iters` register (x9).

The kernel's own prologue (`load_vsrc`: `mov.m.x m0, zero, 0xff` and eight `flw.ps`) is replaced by register-only
instructions with the same end state: m0 = 0xff, f0..f7 = the 256 B image (`fbcx.ps`, per lane under a one-lane mask
when the image is not one number), t0 cleared again so no integer register holds an operand (the integer pipe reads the
x-registers its operand fields name on every instruction, so a word left in t0 would show up there), and for the
accumulating modes f8..f15 = c0. Two macros are given an explicit 4-state net type in [`prelude_e180.sv`](prelude_e180.sv)
(Verilator 5.052 refuses `wire T _din` when `T` is a 2-state `bit`); `-fno-dfg` is `fma_toggle_v2`'s fix. The register
accounting (`ff_acct.sv`, `macros_acct.vh`, `acct.cpp`) is `rtl-sim/fma_toggle_v2`'s, unchanged.

## What it shows (the counts are in `counts-*.jsonl`; `forecast_e180.py` reads them)

- **The issue rate matches the silicon's to about 2%, with no free parameter.** One hart alone (`h1`) issues 0.6208 vector
  ops a cycle (the catalogue's hand-written `spin`, 0.6214; its generated `add` and `fmadd.ps`, 0.581); both harts (`h2`),
  hart 1 started a few cycles late, 0.3808 each (the catalogue's `fadd.ps`, `fadd.pi` and `add`, 0.3730; `nop` 0.3902,
  `spin` 0.3855). `validation-e180.jsonl`, by [`validate_e180.py`](validate_e180.py): 58 cases over loop layouts, start
  skews and contention.
- **The loop's gaps.** With the harts a few cycles apart (any skew of 7-137 cycles tried), every cycle without a result is a
  single-cycle gap between two results: 0.3124 gaps a result (layout A). Started on the same cycle, the harts run in lockstep
  and both hit their loop end together: one 47-cycle gap per iteration, 0.0078 a result, 40 times fewer. Lockstep is not
  stable: any asymmetry between the harts (the random image's two prologues) breaks it. Skews of 7, 23 and 101 cycles give a
  second offset state with some five-cycle gaps (0.281 a result). Over layouts the gaps run 0.266-0.328 a result.
- **fadd.ps: only the write-back returns to zero.** At every gap txfma's result (AND-ed with its valid,
  `txfma_7s/txfma_top.v:1588`), the RF write data (`f8_wdata`, `vpu_bypass.v:221-232`) and the three bypass registers that copy
  it every cycle (`vpu_rf.v:40-46`) fall to zero and rise again: 2 x popcount(result) flips a lane on each of 5 nets a gap.
  The RF's read data holds between reads (the open RTL's register file is a behavioural macro with registered, enabled
  reads), the operands never change, and the sinks are rewritten with their own value. So a one-number fadd.ps flips
  24.995 x popcount(v + v) named bits an instruction, exactly, for every number.
- **fadd.pi: the write-back holds** (the short pipe's F3-F8 enabled flops), so no named class moves. The short pipe's barrel
  shifter is not operand-isolated: it shifts the operand by the instruction's rs2 field (1..7, 0 around the block) on every
  fadd.pi, so its internal nets toggle with the operand's bit pattern (all nets: 23-653 toggles an instruction).
- **The accumulating modes** (c += v): the sum walks, so the write-back, bypass and RF read and store paths switch every
  instruction; counted at three launch points (the sums after 1/6, 1/2 and 5/6 of a 0.4 s launch, `walk_e180.py`), 1,000 or so
  steps a chain each: about 460-570 named flips an instruction in fadd.ps.acc, 181-276 in fadd.pi.acc.

## Files

| file | what |
|---|---|
| `tb_minion_e180.sv`, `prelude_e180.sv`, `Makefile` | the bench (minion_top whole) |
| `asm_e180.py` | the programs: the catalogue's loop for fadd.ps, fadd.pi, the two accumulating modes, and add, nop, spin for the rate check |
| `grid_e180.py`, `cov_e180.py`, `cdiff_e180.py` | the kinds through the bench; coverage summed by hierarchy; a coverage diff by net |
| `validate_e180.py`, `validation-e180.jsonl` | the issue-rate check against the catalogue |
| `counts-primary.jsonl` | every kind, layout A, hart 1 started 50 cycles late, 40,000-cycle window |
| `counts-accpts.jsonl` | the accumulating kinds at the three launch points |
| `counts-layouts.jsonl`, `counts-lockstep.jsonl` | the write-back term's spread: layouts B, o12, o16r, o28, icache contention 8, and lockstep |
| `run_bench_e180.sh` | the grid commands as they ran on the mini |

## Re-make it (on the mini)

```
make CORE_ET=<core-et at b38a1a3> V2=<rtl-sim/fma_toggle_v2> VERILATOR=/opt/homebrew/bin/verilator JOBS=4    # ~35 s
bash run_bench_e180.sh            # the four count files, about 10 min at 3 jobs
python3 validate_e180.py --bin obj_min/Vtb --asm asm_e180.py --out validation-e180.jsonl --jobs 4    # ~3 min
```
The counts are deterministic: the same build and programs give the same lines.

SPDX-License-Identifier: Apache-2.0
