# open-flow/scope — what the board pays besides the arithmetic, with tools anyone can re-run

Q129, 27 October 2026. Companion to [`../txfma/`](../txfma/README.md), which prices one VPU lane's
**multiply-add**. This directory prices the same lane's **transport**: the register files the
operands come out of, the bus that carries them, the result path that carries the answer back, and
the per-lane control — the scope Q128 named as the third reason its bottom-up ledger is a floor.

Same RTL source (public `core-et`, branch `erbium`, the sha `../txfma/setup.sh` pins), same open
7 nm library (ASAP7 RVT, TT), same flow, same operand files, same 0.517 V, **same pinned tool
versions** — so the two ledgers add. Results:
[`docs/reports/data/2026-10-27-q129-ledger-scope/`](../../../docs/reports/data/2026-10-27-q129-ledger-scope/README.md),
method and the two models in its `METHOD.md`.

## Licences

Unchanged from [`../txfma/README.md`](../txfma/README.md): core-et Apache-2.0, ASAP7 and the ORFS
`asap7` platform BSD-3-Clause, the tools ISC/MIT/LGPL/BSD-3. ASAP7 is a **predictive** 7 nm library
from ASU, not the process the ET-SoC-1 was built in.

## Files

| File | What |
| --- | --- |
| `q129_scope_top.v` | the unit under test: one lane's register files, operand bus, result path and control, wired as `vpu_lane.v` wires them for an FP32 TensorFMA32 micro-op. Its header table says which core-et module each part is and where it is instantiated. Two compiled macros the open tree does not contain get a **named model** built from core-et's own `rtl/libs/rf_latches`; a third model stands in for the per-lane half of the control `vpu_ctrl.v` shares across the eight lanes |
| `tb_scope.sv` | the same micro-op stream as `../txfma/tb_gate.sv`, driven at the transport's own ports: A through TENA, B through TENB, the accumulator through the VPU register file at index 2 i + h, the arithmetic's answer supplied at `txfma_res_data`. Two controls, `+accfix` and `+resfix`, hold one field still so a term can be had by difference |
| `synth.sh` | elaborates `q129_scope_top` with yosys-slang and maps it onto ASAP7 RVT TT. Writes `keep` (every boundary) and `mixed` (flattened except the eight scope blocks) — **quote `mixed`**, for the reason `../txfma/README.md` trap 5 gives |
| `pnr.tcl` | OpenROAD: floorplan, place, `repair_design`, CTS, global route, per-net capacitance, then detailed route and extraction. Derived from `../txfma/pnr.tcl` with no recipe change, so the two designs are extracted on identical terms. Detailed routing does not close here either |
| `asap7_seq_behav_scope.v` | behavioural stand-ins for the three ASAP7 sequential cells this netlist uses. `DHLx1` is new and necessary: it is what the latch arrays in `rtl/libs/rf_latches` map to, 3,143 of them |
| `gatesim.sh` | drives the operand stream into the gate netlist under Verilator and writes a SAIF, twice per pattern (`_o1` with the measured ops, `_o0` with none, so the difference is the op) |
| `reduce.sh` | prices all 15 runs with `../txfma/power.py` and then builds the ledger |
| `ledger_scope.py` | the per-part table, the Hamming-ladder fits with standard errors, both controls with what each composite contains, the census join, and what the parts name of Q128's 2.39 pJ rail and 3.84 pJ board gaps — in both readings (see trap 3) |

```bash
export SCRATCH=$HOME/scratch-q129-scope          # anywhere outside a synced folder
export LAB=$PWD                                  # this checkout of et-soc1-prototyping
bash tools/open-flow/txfma/setup.sh              # the same pinned toolchain; ~4 GB
bash tools/open-flow/scope/synth.sh              # ~2 minutes, two netlists
bash tools/open-flow/txfma/mktiles.sh            # the same operand files, with their seeds

python3 tools/open-flow/txfma/census.py --top q129_scope_top \
    --json $SCRATCH/work-scope/syn/scope_mixed.json \
    --cdl  $SCRATCH/asap7cells/CDL/LVS/asap7sc7p5t_28_R.cdl \
    --lib  $SCRATCH/work-scope/lib --out census_mixed.json

NETLIST=$SCRATCH/work-scope/syn/scope_mixed.v PNROUT=$SCRATCH/work-scope/pnr-mixed \
    openroad -no_init -exit tools/open-flow/scope/pnr.tcl

for p in randn zeros ones lq_h0 lq_h1 lq_h2 lq_h4 lq_h8 lb_h0 lb_h1 lb_h2 lb_h4 lb_h8; do
  TILES=$SCRATCH/work/tiles/$p.hex TAG=$p bash tools/open-flow/scope/gatesim.sh
done
TILES=$SCRATCH/work/tiles/randn.hex TAG=randn_accfix MODE=+accfix=1 \
    bash tools/open-flow/scope/gatesim.sh
TILES=$SCRATCH/work/tiles/randn.hex TAG=randn_resfix MODE=+resfix=1 \
    bash tools/open-flow/scope/gatesim.sh

bash tools/open-flow/scope/reduce.sh
```

On a 16-core box at `nice -n 19` with four build jobs, the Verilator build of the gate netlist is
about 15 minutes and the 30 simulations about 20.

## Five things that cost time, so you do not pay them again

The six in [`../txfma/README.md`](../txfma/README.md) all still apply — `--single-unit --compat
vcs`, one `-liberty` per ASAP7 group, no 4× scale on the ORFS platform, hierarchy, `mixed` not
`keep`, pinned tools. These are the ones this directory added.

1. **Only `txfma_top.v` includes `soc.vh`, and none of the VPU files do.** `vpu_bypass.v` opens with
   `` `VPU_LANE_NUM `` and `vpu_input_t` and includes nothing at all. Elaborating it on its own gives
   30 errors that look like a broken file and are really a missing compilation unit. The fix is the
   same as trap 1 for the arithmetic, and it is why `q129_scope_top.v` carries the `` `include
   "soc.vh" `` and goes **first** in `synth.sh`'s file list.
2. **Two of the blocks a multiply-add touches are compiled macros, and they are not in the public
   tree.** `vpu_rf.v` instantiates `vpu_64x32_3r2w_vpurf` and `vpu_tensorc_rf.v` instantiates
   `vpu_tensorc_rf_buffer_array`; neither module exists anywhere in `core-et`. Do not blackbox them
   and quote the rest as a total — the register file is the biggest single item in the transport.
   `rtl/libs/rf_latches` has `rf_latch_3r_2w` and `rf_latch_1r_1w`, the same library's own answer to
   the same job, which is what `q129_scope_top.v` substitutes at the same geometry. **A latch array
   is an upper bound on a macro, by roughly an order of magnitude in area**, so say which rows are
   models in every table.
3. **`zeros` is not an idle baseline here, and the choice is worth a factor of 2.7.** 63% of this
   netlist's switching energy survives with every operand word zero, because the latch arrays' own
   per-entry clock gates and the clock root still run. On a card that floor may already be inside
   the idle the board measurement subtracts. `ledger_scope.py` therefore reports the gap arithmetic
   twice, on the whole netlist and on the data-dependent part alone, and the honest answer is the
   range.
4. **A generate block's instance path carries its index.** `vpu_lane.v`'s two TIMA files come
   through as `LANE_TIMA[0].tenb_rf`, which matches neither `LANE_TIMA/` nor `LANE_TIMA.` — so a
   prefix rule built on `/` and `.` silently folds them into the top-level bucket, where their 334
   latch bits are invisible. `part_of()` matches `[` too.
5. **A census row counts its own children.** `vrf` includes `vrf/arr`, so a per-part join that sums
   depth-1 rows *and* reports the array separately lands the array's 15,685 cells twice. The nested
   rows are subtracted from their parent's part in `ledger_scope.py`.

## What this does not answer

- **the register file's real cost.** The model bounds it from above; nothing bounds it from below
  except zero. A compiled-macro energy figure, or a card measurement of the register file alone,
  is what would close it. E74 in the Q129 series is the register-file-cells experiment;
- **the index term, separated from the data it selects.** `+accfix` moves 1.94 index bits and
  13.75 accumulator-word bits together, exactly as E61's card ladder did, and E61 scored its own
  attempt under-resolved. A design that changes the index while holding the *contents* of both
  registers identical would separate them;
- **leakage**, the fourth item in Q128's list, which this netlist says nothing about;
- **the glitch factor, the coupling capacitance and the unpriced half of the capacitance** — the
  blockers are the arithmetic's, unchanged, and here the unpriced share is worse (63%, against 50%).
