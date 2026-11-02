# tima_bench: the fixed vector-unit bench, counting what int8 runs beside the multiply-add

Q136(c), Mon 2 Nov 2026. This extends [`../fma_toggle_v2/`](../fma_toggle_v2/), Q132(b)'s whole-`vpu_top` bench (core-et's RTL, Verilator with
`-fno-dfg`), with E109's three plusargs ([`tools/claims-v3/e109/desk/tb_patch_e109.py`](../../tools/claims-v3/e109/desk/tb_patch_e109.py):
`+rows`, `+cols`, `+mask`). That bench counted registers. It could not see the register arrays, the scratchpad's reads by size, or which
registers are the TIMA controls. This one counts all three. Results and reasoning:
[`docs/reports/data/2026-11-02-q136c-tima-bench/README.md`](../../docs/reports/data/2026-11-02-q136c-tima-bench/README.md).

**Nothing in the RTL changes.** Every count is read off the RTL's own signals, and two checks show that nothing moved:
- **E109's desk counts, field for field.** On E109's 20 desk streams, all 18 of its fields per stream (cycles, micro-ops, valid slots, scratchpad
  reads, and register bits clocked, changed and seeing an edge, in total and by unit) equal E109's committed `bench-arms.json`.
- **The functional check.** `../fma_toggle_v2/fcheck_vpu.py` run on this binary leaves every accumulator word exact.

## What it adds

| file | what |
|---|---|
| `arrays_acct.sv` | core-et's three array modules, each body verbatim, plus an accounting block that only reads. `rf_latch_1r_1w` holds TenA, the 16 TenB arrays (two per lane, one in each TIMA unit) and TenTMP. `vpu_tensorc_rf_buffer_array` is the 16 TenC macros, int8's accumulators. `vpu_64x32_3r2w_vpurf` is the 8 lane register files. Each counts, per cycle: writes; bits written; storage bits changed; write-data latch openings and their changed bits; reads and reads at a new address (macros); and read-address and read-data toggles. A negedge shadow counts the latches' storage changes a second, independent way |
| `macros_line.vh`, `ff_acct_line.sv` | the register macros instrumented as in `../fma_toggle_v2/macros_acct.vh`, with each register's source line added, so that a named group can be summed. The TIMA controls are the registers on `tima_clk_en = working && req_int8` (`vpu_tensorfma.v:841-929`) |
| `acct_line.cpp` | `../fma_toggle_v2/acct.cpp`'s unit tallies, unchanged, plus the per-line tallies, the arrays' tallies and a JSON dump (`ACCTARR`, `ACCTLINE`) |
| `tb_patch_q136c.py` | the testbench additions: the scratchpad reads by size (32-, 64- and 256-bit) and the toggles on its 256-bit read bus; the TenA, TenTMP and TenB write buses; TenC's read enable, `tima_clk_en` and `working`; the lanes' TIMA clock-gate enables (`ACCTX`). Two plusargs: `+pre=<n>` runs n int8 ops before the stream (as on a card, where an fp32 run follows int8 runs), and `+firstall=1` sets first_pass on every op |
| `build.sh` | copies the bench and the files above into a scratch directory, applies E109's patch and this one, and builds lean (no coverage, no trace), as E109's desk did |
| `run_streams.py` | every stream of E109's and E124's design at the card's cycles per op; E109's desk streams at the FSM's own pace, compared field by field with E109's committed counts; the fp32 streams after an int8 run; and desk-only arms |
| `price.py` | makes the counts per second at each card's measured op rates, and prices the candidates at the bench's constants (M2, M4, I3) |

## Build and run

```
VERILATOR=<verilator> CXX=/usr/bin/clang++ JOBS=6 bash rtl-sim/tima_bench/build.sh <scratch>          # from the repo root
python3 rtl-sim/tima_bench/run_streams.py --bin <scratch>/obj_q136c/Vtb --out counts.json --jobs 6       # 65 streams, about a minute on 6 cores
python3 rtl-sim/tima_bench/price.py --counts counts.json --out-json priced.json --out-md priced.md
cd rtl-sim/fma_toggle_v2 && PYTHONPATH=. python3 fcheck_vpu.py --bin <scratch>/obj_q136c/Vtb --out fcheck-vpu.json --ops 4 --seeds 3 --jobs 6
```

Standard library only. On the desk machine used here: Verilator 5.052 (conda-forge), Apple clang 21; core-et `b38a1a31`.

## What it still cannot see

- **The scratchpad is the bench's array**, answering in two cycles and never refusing. So the read *requests* are the RTL's: their number,
  their size and their address bits. The dcache's SRAM, its own read energy and its data bus between reads are not in the bench. The read bus's
  toggles are those of this bench's model, which drives a 256-bit chunk on every read.
- **The core is one start pulse and a control word.**
- **A macro's own access.** The TenC macro and the lane register file are behavioural models. The bench sees their read enables, addresses and
  output registers, but not what a read costs inside the macro.
- **Zero delay, so no glitches.** Data toggles are settled values.
- **This is core-et, the Erbium branch:** a later revision of the ET-SoC-1's lineage, not the ET-SoC-1's own.
