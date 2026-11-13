# The counter on sparse parity: the kernel's own counts reproduced, and its L1 solve counted (Q166, Thu 12 Nov 2026)

Q166's step 2 (the counter, [`tools/counter/`](../../../../tools/counter/README.md)), validated on sparse parity
([`workloads/sparseparity/`](../../../../workloads/sparseparity/README.md)). Simulator runs only, on aifoundry3's host
CPU: no card, device node, card lock or device command; `et-who` read "No process holds an ET-SoC-1 device node or card
lock" before every build and run; host load 0.4-2.3 on 16 CPUs; one job of ours at a time; every file in a new folder of
our own. The kernel is the 29 Sep card runs' file, byte for byte (`kernel/kernel.sha256`).

*Dated note (Thu 12 Nov 2026, Q166's fix lane, on its verifier's findings).* The runs below were first made 15:30-16:38 PST
with the counter as it then was. They were made again 19:12-19:20 PST by the fix lane, with the fixed counter, on the same
binaries and arguments, and those re-runs are what this folder holds.
- Every field of the first counts files reproduces exactly (`first-runs-regression.txt`, with the first files' sha256).
- The re-runs add the firmware's work outside the kernel, CSR names and branch direction changes.
- The fix lane also ran two kernels that store tensors (`tensor-store/`, below).

## Results

**Every count the kernel reports about itself is reproduced exactly** (*desk check of code against the simulator's own
run*; `validation.json`, `tools/counter/validate_sparseparity.py`). Per working minion, in 9 runs (7 with the
profiling simulator, `runs/`; 2 with the installed one, `runs-installed/`). The counter backs 12 minions: 11 tensor
minions in 8 runs, and the scalar run's minion through S1c:

| Run | Path | Minions | T1: int8 ops outside `recompute` = `work` | T2: rescans (not in `work`) | G1: publishes = row tiles | G2: poll loads - busy polls = tiles - nbuf |
|---|---|---|---|---|---|---|
| c0-tensor | M4, n 32, k 3, m 128 | 1 | 74 = 74 | 8 | 30 = 30 | 267 - 239 = 28 |
| s4-tensor | M4, n 48, k 3, m 256 | 1 | 420 = 420 | 24 | 68 = 68 | 466 - 400 = 66 |
| k4-2shires | M4, n 40, k 4, m 192, 2 shires x 2 | 4 | 2,646 = 2,646 | 84 | 572 = 572 | 4,549 - 3,985 = 564 |
| l1b-s0 | variant b, L1 (512, 4, 0.3, 448), slice 0 of 20,000 | 1 | 5,152 = 5,152 | 70 | 23 = 23 | 5,580 - 5,559 = 21 |
| l1b-s10000 | the same, slice 10,000 | 1 | 4,389 = 4,389 | 49 | 57 = 57 | 4,370 - 4,315 = 55 |
| l1b-s19999 | the same, the last slice | 1 | 1,113 = 1,113 | 77 | 159 = 159 | 202 - 45 = 157 |
| c0-scalar | scalar | 1 | S1c: the counter's executions at each of the 3 addresses of `++acc->count` (sparseparity.c:324) = the record's 4,960; S1: the records' 4,960 = the host's (no counter in it) | | | |

Also: every int8 op paired with one B load (T3), 16,384 MACs an op (T4), and the plan's op count (T1_plan), in every
tensor run. The installed simulator's runs (`runs-installed/`, the same two M4 cases) pass the same checks.

**The profiling simulator emulates exactly what the installed one does** (*desk check*): the per-PC counts of all 64
harts of c0-tensor and of s4-tensor, branch directions included, are identical from both (`count_kernel.py compare
runs/c0-tensor/counts-log.json runs-installed/c0-tensor/counts-log.json` prints IDENTICAL), and so are the counts
from two builds of it. Results, sums and candidates match the 29 Sep simulator runs
(`workloads/sparseparity/data/2026-09-29-aifoundry3-sysemu-r4/`, `-sysemu-m4/`). Timing-only fields differ: the
kernel's cycle record for c0-tensor reads 68,073 here and 68,201 from the installed simulator (and on 29 Sep): 128,
the late-carry correction `fixcyc` toggling with the launch's start cycle; wait and copy cycles move by a few hundred
from run to run of the same build.

**The L1 solve the card measured** (variant b, 29 Sep, `workloads/sparseparity/data/2026-09-29-aifoundry3-m5-energy/m5/
m5-l1-b.*`: 1,024 minions, 81,989,040 int8 ops, 1,381,776 row tiles, 0.1353 s at 598.8 MHz), against three simulated
slices of it (`card-compare-l1b.json`, `tools/counter/card_compare_sparseparity.py`; *post hoc, an estimate scaled by
every minion's ops and row tiles from the card's records*):

| Quantity | Counted (simulator, work only) | Cycle model, fitted (`tools/cycle_model.py`) | Instructions per cycle |
|---|---|---|---|
| hart 0, per row tile | 1,032 | 3,139 (H_TILE) | 0.33 |
| hart 0, per output tile (the epilogue) | 810 | 1,606 (E_OUT) | 0.50 |
| hart 0, per op (the tensor unit) | (one CSR write) | 378 (C_OP, streamed A) | |
| hart 1, per row tile (row generation) | 3,469 | 16,296 (variant b's prediction) | 0.21 |
| median minion: hart 0 + hart 1 | 10.7 M + 4.7 M | 77.4 M measured cycles | 0.199 |
| hart 1, fitted with an intercept (fix-q166) | 3,139 a row tile + 26,310 a launch | 16,296 | 0.19; the median minion's occupancy 0.193 |

The fit of hart 1 through the origin leaves residuals of +28,972, -6,192 and -22,780 instructions on the three slices
(27% on slice 0); with an intercept they are +10,258, -13,678 and +3,419. So read the median minion's occupancy as
0.193-0.199 (`card-compare-l1b.json` › `counted_rates.hart1_fit_with_intercept`, `comparison`).

`work` leaves out the spin loops (the polls in `wait_count`, found by source line in `kernel/all-addr2line.txt.gz`):
they follow the simulator's timing, not the card's (0.04-81% of a hart's counted instructions in the slices). The
counted instructions fill a fifth of the card's issue slots; the rest of the time is the tensor unit and waiting, which
only a cycle model or the card's cycle counter gives.

**The ledger's counts for that one solve** (`card-compare-l1b.json` `per_solve`; *estimate, post hoc*): 15.7 G work
instructions: scalar integer 5.85 G, vector integer 3.37 G, loads 2.21 G, stores 0.86 G, branches 0.72 G taken and
0.50 G not taken, float-integer moves 0.60 G, tensor CSR writes 0.44 G, jumps 0.40 G, masks 0.36 G, `fswg.ps` staging
stores 0.31 G, multiplies and divides 0.08 G (per-class fit residuals at most 6% except branches, 15%). Tensor unit:
81,989,040 int8 TensorIMA8A32 ops as the kernel counts them plus about 1.3 M rescans; 16,384 MACs an op; each op loads
2,048 B (A and B tiles) from the shire's own scratchpad; hart 1 stages 7,168 B a row tile into it with `fswg.ps`, a
global store into the own scratchpad by its explicit shire address (the catalogue prices `fswl.ps`, not `fswg.ps`; the
first text of this README said `fswl.ps`); the X_B copy-in moves 229,376 B from DRAM into each shire's scratchpad a
launch (`TensorLoadL2SCP`, its chunks dealt to the shire's minions; the slices ran one minion a shire, which copied its
shire's whole share), so 7,340,032 B a launch on the card's 32 shires.
Which cache level served the L1-path loads and stores is not in the simulator: the card's counters give it
(`tools/counter/README.md`, "Bytes by level").

## What ran

| Step | Where | What |
|---|---|---|
| the profiling simulator | aifoundry3, a new folder of ours | `tools/counter/build_profiling_sysemu.sh` twice (two folders, byte-identical): `build/BUILD-INFO.txt` |
| sparse parity | the same folder | `cmake -S workloads/sparseparity -DCMAKE_PREFIX_PATH=<folder>/prefix` (the shadow prefix); `.text` `3e14be32…`; `spp_selftest` PASS |
| the same kernel with `-g` | the same folder | the toolchain's own flags plus `-g`: `.text` `3e14be32…` again; addr2line for every address (`kernel/`) |
| 7 counted runs | the same folder | `tools/counter/run_counted.sh` (the log streamed into the counter, the profile kept): `runs/<case>/RUN.txt` |
| 2 runs, installed simulator | the same folder | a host built against `/opt/et`, `run_counted.sh --no-prof`: `runs-installed/` |
| validation and the card comparison | the Intel, desk | `validate_sparseparity.py`, `card_compare_sparseparity.py`, from the files here |
| the landed tools, once more | the box | c0-tensor again with `tools/counter/` as first staged: counts identical at every PC to the first `runs/c0-tensor` |
| every run again, fixed counter | aifoundry3, the fix lane's own folder, 19:12-19:20 PST | the same binaries and arguments, `tools/counter/` as fixed: every field of the first counts identical (`first-runs-regression.txt`); these are the runs kept here |
| the profile route, again | the Intel, desk | `count --prof` with `--pc-offset auto` (it finds 0x335000 in every run, the scalar one included), with and without `--assume-no-wait`: `profile-route.json` |
| two kernels that store tensors | aifoundry3, the fix lane's folder, 19:12 and 19:27 PST | `tensor-store/` (below) |

Each `runs/<case>/` holds `out.json` (the host's JSON line), `records.bin` (`--records-out`: 64 B a hart),
`counts-log.json` (the counter, log mode), `prof.txt.gz` and `counts-prof.json` (the block profile and the profile
route's counts, `--pc-offset auto --assume-no-wait`), `counter.out` and `RUN.txt`. The profile route resolves 56.7-78.9% of the
working harts' instructions with default flags and 66.6-93.2% with `--assume-no-wait`, never above the log at any PC,
every idle hart exact (`profile-route.json`): a lower bound by this check, not by proof (its no-wait equation does not
know the FP/vector stall, `tools/counter/README.md`). `kernel/sparseparity.dis` is the ET objdump with its first line's build path cut;
the counts were made from the uncut file, which differs in that line only (the parser reads instruction and symbol
lines; a profile recount from this file gives identical counts).

## Tensor stores (fix-q166)

The first counter crashed on every TensorStore line (`addr` and `stride` printed as hex without `0x`), and sparse parity
issues none. The fix lane ran two kernels that do, built in its own box folder against `/opt/et` and logged into the fixed
counter. Desk expectations are written from each kernel's source before reading its counts.

| Run | Kernel | Expected (desk, from the source) | Counted | Host |
|---|---|---|---|---|
| `tensor-store/ts-gemm1-int8` | E101's GEMM (`tools/claims-v3/rgm`, `.text` `e381c358…`), `--values gemm1:tiles:<int8 full tile> --shires 0x1 --per-shire 32` | one TensorStore of 16 rows x 64 B per 32 ops: 2,048 ops, so 64 stores, 65,536 B, to DRAM | 2,048 int8 ops (33,554,432 MACs), 64 stores, 65,536 B, all DRAM | rc 0; its C check exact (8,192 of 8,192 words) |
| `tensor-store/ts-probe` | `workloads/onchip`, `--test probe --method 0 --shires 0x1` (`.text` `f743e9ef…`) | two TensorStores of 16 rows x 32 B per minion into its own scratchpad: 64 stores, 32,768 B | 64 stores, 32,768 B, all own scratchpad | the write launch ran; the host then aborted (rc 134, `dev::Exception` in the runtime's response thread), and it aborts the same way without the log (`rc-plain-run.txt`): a host or runtime fault in the simulator, not the counter's. Its counts cover the write launch |

Both runs' `outside_kernel` show the firmware's work around each launch: M 32,002 + S 67,858 instructions on shire 0's
64 harts for the GEMM (the same as every sparse-parity run here), 2 TensorIMA8A32 and 3 TensorLoads a minion.
`rgm.dis` and `onchip.dis` are the kernels' objdumps.

## Departures and incidents

- A Release build of the simulator's source does not link (`mmu.cpp`'s `inline effective_execution_mode`); built as
  the installed binary was, without `-O`.
- `-dump_prof` passed to the `sys_emu` executable never reached the emulator: a `--sysemu` host runs it inside its own
  process from `libsw-sysemu.a`. Hence the shadow prefix.
- A first profiling build without `-fmacro-prefix-map` ran the same seven cases first; its counts were identical at
  every PC to the runs kept here; it is superseded.
- The fix lane's re-runs (19:12-19:20 PST) replace the first runs. Their records differ from the first runs' in timing
  fields only: the cycle record by 128 (the `fixcyc` carry), hart 0's wait and copy cycles by up to 1,664, and the status
  word's launch-epoch bits. Their profiles differ in the cycle column and in landings outside the kernel; every count is
  identical.
- The onchip probe's host aborts after its write launch in the simulator, with or without the log (above).

SPDX-License-Identifier: Apache-2.0
