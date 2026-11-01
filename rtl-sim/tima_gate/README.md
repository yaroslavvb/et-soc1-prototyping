# tima_gate: the real vector unit with its int8 multiply-add as gates

Q133(a), Sun 1 Nov 2026. [`rtl-sim/fma_toggle_v2`](../fma_toggle_v2/) runs core-et's whole `vpu_top` and returns correct multiply-adds, but
int8's multiply is one line of behavioural RTL (`tima/tima_top.v:89`, `$signed(a) * $signed(b)`), so that bench sees int8's operands, products
and sums and no net inside the multiplier. This directory builds the same bench with `tima_top` (16 per VPU: two a lane) replaced by a
gate-level netlist from the open flow ([`tools/open-flow/tima/`](../../tools/open-flow/tima/)), and, for a like-for-like comparison, with
`txfma_top` (the float unit, 8 per VPU) replaced instead. Results: [`docs/reports/data/2026-11-01-q133a-int8-gate-level/`](../../docs/reports/data/2026-11-01-q133a-int8-gate-level/README.md).

**Nothing of the bench is rewritten.** `tb_vpu.sv`, `ff_acct.sv`, `acct.cpp`, `macros_acct.vh`, `accum.c`, `settle_count.cpp`, `run_kinds.py`
and `train_maps.py` are `../fma_toggle_v2`'s, used from there. The Makefile lists the netlist and the cell models before the RTL, so the
netlist's `tima_top` (or `txfma_top`) is the one elaborated and the `-y` search never reaches the RTL file. `-fno-dfg` stays (Q132(b)'s fix).

**What the netlist changes, and what it does not.**
- The unit's nets are the netlist's: one scalar name per physical net (`netlist_stages.py`), named for its stage in the RTL bench's own convention
  (`f2_in_*` operand, `f2_prod_*` multiplier, `f3_add_*` adder, `ctl_*` control; the ports keep their names), every wire public so the
  simulator cannot fold two nets into one trace. The float netlist has no stage split, and its gated clocks are named `clk_*`, so the counter
  drops them as it drops the RTL's clock names.
- The cells are one `assign` each, written from ASAP7's liberty functions (`liberty_models.py`), with tracing off inside them: a VCD holds the
  netlist's nets and not the cells' ports again.
- **The unit's own registers stop reporting to `acct.cpp`**: they are flip-flop cells now, not the `FF` macros. The register counts for the
  unit (`ff.tima`, or `ff.txfma`) read 0 in a gate run; the analysis takes them from the RTL run of the same tile, which has the same registers
  and the same stimulus.
- Everything else in the VPU is the RTL, so a whole-VPU count is the RTL's rest plus the gate-level unit.

## Build and run

On the Intel (macOS x86_64), with Verilator 5.052 from conda-forge, whose archiver is only in its env:

```
export PATH="$HOME/.local/micromamba/envs/verilator/bin:$PATH"
V="VERILATOR=$HOME/.local/micromamba/envs/verilator/bin/verilator CXXOVERRIDE=/usr/bin/clang++"
make BUILD=<dir> CORE_ET=../../external/core-et $V tools                    # accum, settle_count
make BUILD=<dir> CORE_ET=../../external/core-et $V rtl                      # the control: fma_toggle_v2's bench, flag for flag
make BUILD=<dir> CORE_ET=../../external/core-et NETDIR=<netlists> ARM=booth_tree $V gate     # about 3 min with 6 jobs, unloaded
make BUILD=<dir> CORE_ET=../../external/core-et NETDIR=<netlists> FNET=txfma_flat JOBS=2 $V gatef
BUILD=<dir> OUT=<dir> LAB=<this checkout> MAPS=full KPOINTS=launch BITS=all bash run_arm.sh booth_tree
```

`NETDIR` holds `asap7_cells.v` and the `*_staged.v` netlists that `tools/open-flow/tima/` writes; the data directory has the netlists gzipped.
`run_arm.sh`'s header lists its knobs (which kinds, which single-bit tiles, which launch points, full or one-stream maps). **No count may be
quoted from a run that fails the check**: `run_kinds.py` compares every accumulator word with software after each measured op.

| File | |
|---|---|
| `Makefile` | the control, the gate-level int8 bench (`gate`), the gate-level float bench (`gatef`), the two tools |
| `run_arm.sh` | one binary through the int8 kinds and the single-bit tiles (E79's A list, E102's B list and masks), or the float kinds |
