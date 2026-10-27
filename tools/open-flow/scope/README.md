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
| `ledger_scope.py` | the per-part table with each part's clock/signal split, the Hamming-ladder fits with standard errors **against both benches' bus counters** (`--acct-arith`, trap 8), both controls with what each composite contains, the census join, the internal-mix sensitivity (`--cell-energies`), the card's `zeros` bound on the models (trap 6), and what the parts name of Q128's 2.39 pJ rail and 3.84 pJ board gaps — as a range over the clock-net term (trap 3) |

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

## Eight things that cost time, so you do not pay them again

The six in [`../txfma/README.md`](../txfma/README.md) all still apply — `--single-unit --compat
vcs`, one `-liberty` per ASAP7 group, no 4× scale on the ORFS platform, hierarchy, `mixed` not
`keep`, pinned tools. These are the ones this directory added; 3 and 6–8 were learned the hard way,
from an adversarial verification of the results directory the same day it was published.

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
3. **`zeros` is not an idle baseline here — and it is not a clock-only baseline either.** 63% of
   this netlist's switching energy survives with every operand word zero, and the first version of
   this file said that was the latch arrays' clock gates and the clock root. It is not: the split
   is **34% clock nets, 66% signal switching**, because the accumulator index keeps sweeping
   2 i + h (`idx_toggles` = 992 per op in every pattern, `zeros` included) and a 64-entry read mux
   tree switches on the index with zero data. Only the clock part could already be inside the idle
   a board measurement subtracts; a card sweeps the index too. So `ledger_scope.py` reports the gap
   arithmetic as a **range over the clock-net term** (`transport_switching_plus_internal_pJ_per_mac`
   down to `transport_excl_clock_nets_with_internal_pJ_per_mac`, 1.48 → 1.26 pJ/MAC) and keeps the
   data-dependent figure as a separate quantity, not as the bottom of that range. Check a
   zero-operand figure's clock/signal split before you call it a clocked floor.
6. **A card measurement can bound a model from above, and it is worth looking for one.** The
   latch-array register file is "a ceiling" — but the board's own `zeros` run (0.27 pJ per
   multiply-add over idle, whole board) costs *less than this one lane's transport model does in
   the same stimulus*, by 2.4×. `ledger_scope.py` now runs that check
   (`gap.card_zeros_bound`) and it changes what the model's numbers may be used for. A model block
   is worth checking against every card number whose stimulus it shares, not only against the one
   it was built to predict.
7. **A counted bit and a designed bit are different units.** The `+accfix` control drags 13.75
   counted accumulator-read bits along with its 1.94 index bits, and subtracting them at the
   *designed*-bit ladder slope — fJ per designed h-flip — put the index-alone bound at 72–136 fJ
   where the per-counted-bit slope puts it at 166–175 fJ, reversing the conclusion. The two
   regressors are both in `ladder.<fam>`; pick the one whose denominator matches the bits being
   subtracted.
8. **Two benches on the same operand files do not have to agree on a toggle count.** This bench's
   `bus_toggles` and `../txfma/tb_gate.sv`'s differ by −26% to +40% per ladder rung while agreeing
   to 0.3% on `randn`. Before adding two slopes fitted on two counters, refit one of them on the
   other's counts (`--acct-arith`).
4. **A generate block's instance path carries its index.** `vpu_lane.v`'s two TIMA files come
   through as `LANE_TIMA[0].tenb_rf`, which matches neither `LANE_TIMA/` nor `LANE_TIMA.` — so a
   prefix rule built on `/` and `.` silently folds them into the top-level bucket, where their 334
   latch bits are invisible. `part_of()` matches `[` too.
5. **A census row counts its own children.** `vrf` includes `vrf/arr`, so a per-part join that sums
   depth-1 rows *and* reports the array separately lands the array's 15,685 cells twice. The nested
   rows are subtracted from their parent's part in `ledger_scope.py`.

## What this does not answer

- **the register file's real cost.** The model bounds it from above, and the card's own `zeros`
  measurement bounds the model: one lane's transport model costs 2.4× what the whole board costs
  per multiply-add on that pattern, so the model **over-prices** and nothing yet bounds the real
  figure from below except zero. A compiled-macro energy figure, or a card measurement of the
  register file alone, is what would close it. E74 in the Q129 series is the register-file-cells
  experiment;
- **the index term, separated from the data it selects.** `+accfix` moves 1.94 index bits and
  13.75 accumulator-word bits together, exactly as E61's card ladder did, and E61 scored its own
  attempt under-resolved. A design that changes the index while holding the *contents* of both
  registers identical would separate them;
- **leakage**, the fourth item in Q128's list, which this netlist says nothing about;
- **the glitch factor, the coupling capacitance and the unpriced half of the capacitance** — the
  blockers are the arithmetic's, unchanged, and here the unpriced share is worse (63%, against 50%).
