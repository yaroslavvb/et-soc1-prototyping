# The counter: a kernel file's run turned into the energy ledger's counts (Q166, step 2)

The energy manual prices events: instructions by class, bytes by memory level, tensor operations by format. Until now
a person wrote a program's counts down by hand. This folder turns a kernel file into those counts: it runs the
kernel in the functional simulator (`sys_emu`, et-platform's open emulator, the same kernel file the cards run),
streams the simulator's instruction log into a parser, and prints every executed instruction by the manual's
classes, per hart and in total, with every tensor operation by format and shape and every memory access by address
region. It also builds a profiling simulator (the per-block profile option, compiled out of the lab boxes' installed
binary) and reads its block histogram, a cheaper second route that is exact only where its equations close.

**Results first** (Thu 12 Nov 2026; simulator runs on aifoundry3's host CPU, no card; data in
[`docs/reports/data/2026-11-12-q166-counter-sparseparity/`](../../docs/reports/data/2026-11-12-q166-counter-sparseparity/README.md)):

- **The counter reproduces every count sparse parity's kernel reports about itself, exactly**, on 9 simulator runs
  with 12 working minions:
  - On 11 tensor minions in 8 runs (M4's tensor kernel: one minion twice in each simulator and four minions on two
    shires; variant b on three slices of the L1 instance the card solved), four counts match:
    - hart 0's TensorIMA8A32 count (`work`) = the int8 TensorFMAs the counter saw outside `recompute`;
    - hart 1's row tiles (`count`) = its publishes;
    - hart 1's busy polls (`wait`) = its poll loads less one per row tile after the first `nbuf`;
    - the plan's op count.
  - On the scalar run, each hart's candidates (`count`) = the counter's executions at every address of the
    `++acc->count` line (S1c, 4,960).
  - The scalar run's S1 compares the records with the host; no counter enters it.

  *Desk check of code against the simulator's own run; the sites are found by source line (addr2line on a `-g` build with the same `.text`).*
- **It also counts what the kernel does not report**: the tile rescans (`recompute`) issue 1.1-10.8% more
  TensorIMA8A32 ops than `work` says (8 on 74, 24 on 420, 84 on 2,646, 70 on 5,152, 49 on 4,389, 77 on 1,113), each
  paired with its B load. *Simulator count.*
- **The profiling simulator behaves as the installed one**: same revision (et-platform `353f20e`, which the installed
  library's member list and symbols match), same compiler and flags plus the profile; its help differs by the one
  `-dump_prof` line, its static library's members by `profiling.cpp.o`; two builds in two folders are byte-identical; and the installed
  simulator's instruction log gives the same count at every PC, branch direction included, on every one of 128 logged
  harts of two runs. *Desk checks.*
- **Instructions are not seconds.** On the card's L1 solve (variant b, 29 Sep, `m5-l1-b`), the counted work
  instructions of the median minion (10.7 M on hart 0, 4.7 M on hart 1; spin loops left out) fill 0.199 of its
  77.4 M measured cycles. Per unit, the counter's instructions against the cycle model's fitted cycles: hart 0's row-
  tile overhead 1,032 against 3,139 (0.33 per cycle), its epilogue 810 per output tile against 1,606 (0.50), hart 1's
  generation 3,469 per row tile against the model's 16,296 for variant b (0.21). *Post hoc; scaled from three
  simulated slices to every minion's ops and row tiles in the card's records.* A forecast of seconds still needs the
  cycle model; the counter gives it its inputs.
- **The profile route is a lower bound by check, not by proof** (`profile-route.json`):
  - It resolves 56.7-78.9% of the working harts' instructions with default flags, and 66.6-93.2% with `--assume-no-wait`.
  - It was never above the log at any PC (7 runs, both flag sets), and every idle hart is exact.
  - Its automatic offset finds the kernel in every run, the scalar one included.
  - Its no-wait equation does not know the FP/vector stall (below).

  Use the log for counts.

## Builds on

*(The rule of the Q145 stock-take, MAP section 3.)* **Checked:** the prior-work inventory, read Thu 12 Nov 2026; rows
P05, P11, P19, P24, P27, L02, L03, L06, L13 and H04. **Used:** P05 sw-sysemu (et-platform `353f20e`, the lab cards'
firmware commit; its PROFILING option, `sys_emu/profiling.cpp`, the DEBUG instruction log of `insn_util.h`, the
memory map of `memmap.h`); P27 and L02 for the stock counters (`docs/research/counters-and-dram.md`, the counter carry
`rtl-sim/pmu_carry`, `workloads/pmcsel`), with `workloads/nocroute` and `workloads/memprobe` as the kernels that already
read the shire-cache and memory-shire monitors through system calls 9 and 10; L06 for the classes
(`docs/energy-manual/03-instructions.md`, `03a-every-instruction.md`, `04-bytes-memory.md`); L13 for sparse parity
(`workloads/sparseparity`: its kernel, records, `sysemu_check.sh`, `tools/cycle_model.py`, the card runs of 29 Sep).
Checked against an earlier measurement: the kernel's own report in the same run, and the 29 Sep simulator runs'
results (`data/2026-09-29-aifoundry3-sysemu-r4/`, `-sysemu-m4/`: identical op counts, sums and candidates).
**Not used:** P19 and P24 (cycle estimators for compiled networks: not a kernel's instruction counts); patch 0003
(counter events by choice need firmware on the card: NO-GO, `patches/README.md.dated-note-1.md`). **Tiers:** public
pieces only. **Readiness:** a tool, not a registration; nothing here is frozen for a blind test.

## The profiling simulator

`sw-sysemu`'s CMake option `PROFILING=ON` only adds `sys_emu/profiling.cpp` to the sources (CMakeLists.txt line 176).
The hooks are behind two defines the CMake build never sets (the old `sys_emu/Makefile` sets both when `PROFILING=1`):

- `BEMU_PROFILING`: every taken branch, jump, trap and return calls `profiling_write_pc(hart, new PC)` (`insn_util.h`
  `WRITE_PC`); without it the call is an empty inline stub, which the installed binary still carries.
- `SYSEMU_PROFILING`: the `-dump_prof <path>` option and the dump when the simulation ends (`sys_emu.cpp`,
  `sys_emu_parse_args.cpp`, `sw-sysemu/SysEmuImp.cpp`).

The dump is one line per hart and landing PC: `<hart> <pc hex> <landings> <emulated cycles to the hart's next landing>`.

**Build it** with [`build_profiling_sysemu.sh`](build_profiling_sysemu.sh) (a lab box with the ET install, or any Linux
with it): `CMAKE_BUILD_TYPE` empty (no `-O`, no `-g`: the installed binary carries the un-inlined stubs of such a
build, and a Release build of `353f20e` does not link, because `mmu.cpp` defines `effective_execution_mode` `inline`;
upstream fixed it in `d4d830f00`), `PROFILING=ON`, `CMAKE_CXX_FLAGS='-DBEMU_PROFILING -DSYSEMU_PROFILING
-fmacro-prefix-map=<folder>/src/=/'` (the last keeps the build folder out of `assert()` strings; it maps to `/`, not to
`/usr/src/et-platform/` as the installed build's strings read, so 41 non-hook members differ from the installed ones in
those strings only; mapping to `/usr/src/et-platform/` would make every non-hook member match, and is not done here so the
two recorded builds stay reproducible). Source: et-platform
`353f20e982f4efd99019d04f8022681cc727c4f2`, `sw-sysemu` tree `877c09cf1c0c`, exported with `git archive` (tar sha256
`737a1166b615a3b4e3ac48e26a1ecc1e5b35ab5c286abcdc291f838851178451`). Built on aifoundry3 (cmake 3.28.3, GCC 13.3.0, the
installed binary's compiler family) twice, in two new folders, byte-identical:

| File | sha256 |
|---|---|
| `prefix/bin/sys_emu` | `ce4469ea430ff3134a6c9f03d9be308dff7a38d1be111691e7f993b5a63e333b` |
| `prefix/lib/libsw-sysemu.a` | `4504bd0a585e33e55def57f8f7898d416f3077b1ecbc41a37748311f44ae9508` |
| installed `/opt/et/bin/sys_emu` (for reference, not rebuilt) | `fc2be7c30612b624cf08c795425a172658eed9ec25ecacd2be057648bb0f75bb` |

**The emulator runs inside the host program.** A host started with `--sysemu` does not run the `sys_emu` executable:
the runtime's device layer links `libsw-sysemu.a` and runs the emulator in a thread of the host, passing the
`--sim-args` words to the same option parser (it rejects `-dump_prof` when the library lacks it). So a host is
profiled only when it is linked against the profiling library. The script therefore leaves a **shadow prefix** beside
the build: `prefix/bin` and `prefix/lib` are folders of links to the installed tree with this build's `sys_emu` and
`libsw-sysemu.a` in them, and every other entry links to the installed tree. Build a host against it with
`-DCMAKE_PREFIX_PATH=<folder>/prefix`; its CMake files find everything there, and the kernel it builds is unchanged
(sparse parity's `.text` sha256 stays `3e14be32…`, its ELF `65dd07da…`, both the 29 Sep build's).

The instruction log needs no rebuild: `-l` is compiled into the installed library too, and a host built against the
installed tree logs the same way (`run_counted.sh --no-prof`).

## Counting a kernel

```bash
# on the box: the kernel's disassembly with the ET toolchain (it knows the ET instructions and CSR names)
/opt/et/bin/riscv64-unknown-elf-objdump -d -w kernel.elf > kernel.dis
# one counted run: the host's own command after --, with @SIM@ where its simulator options go
bash tools/counter/run_counted.sh --dis kernel.dis --out RUNDIR --log-sel '-ls 0,ffffffffffffffff' -- \
    build/x/host/x_host --sysemu --sim-args @SIM@ <the host's arguments>
python3 -I -B tools/counter/count_kernel.py table RUNDIR/counts-log.json
```

`run_counted.sh` makes `sysemu.log` a FIFO in the run folder (the runtime writes the emulator's log there, `-lp` being
reserved), starts `count_kernel.py count --log` reading it, runs the host, and keeps `counts-log.json`, the profile,
the host's JSON and `RUN.txt`. Nothing of the log is written to disk: about 400 B an instruction would be 1-2 GB for a
few million instructions. The runs here took 37-58 s with the log (a run with the profile alone, 35 s). Log the shires that
work (`-ls <shire>,<64-bit hex mask of its harts>`, repeatable; `-lt <hart>`); harts that are not logged are not
counted. A host needs a `--sim-args` option (sparse parity, sparsity, sgemm, enercat, memhier, memprobe, nocbench,
nocroute and onchip have one).

**The output** (`counts-log.json`, schema `ledger-counts/1`) per hart and in `total`:

- `instructions`, `compressed_instructions`, `by_class` (below), `by_mnemonic` (objdump's names);
- `tensor`: per kind (`fma_fp32`, `fma_fp16`, `fma_int8`, `load`, `load_tenb`, `load_l2scp`, `store`, ...) its `ops`,
  and `macs` (arows x K x bcols, from the simulator's own start line) or `bytes` with `bytes_<region>`;
- `memory`: per class and address region, reads and writes and their bytes;
- `per_pc`: `[executions, taken]` for every executed PC (taken only for conditional branches), the raw counts;
- `killed_and_restarted` (an instruction the simulator retried: retired once), `cycles_span` (the emulated cycles from
  the hart's first kernel instruction to its last; equal to its instructions when it never waited);
- `by_csr`: CSR accesses by instruction and CSR name (`csrr hpmcounter3`, `csrw tensor_store`, ...), which `by_mnemonic`
  lumps together;
- `branch_direction_changes` and `branch_changes_per_pc` (log mode): how often a conditional branch's outcome flipped
  from one execution to the next. 03a prices a branch that follows the data at about 2.5x a predictable one; a sort's
  merge is such a branch.
- `outside_kernel` (log mode, top level): what the logged harts retired outside the kernel's U-mode text, by privilege
  mode, with its tensor ops and memory traffic. That is the firmware around each launch: on every shire-0 run here,
  M 32,002 + S 67,858 instructions (1,560 a hart), 2 TensorIMA8A32 and 3 TensorLoads a minion, and about 0.3 MB of memory
  traffic. It is never in `harts` or `total`; a card's retired-instruction counters include it (below).

Read with care:
- `memory["tensor"]` shows the bytes the tensor instructions moved as the simulator's MEM lines show them: the same bytes
  as the `tensor` block's `bytes_*` (plus a TensorLoadL2SCP's write into the scratchpad). Never add the two.
- A masked tensor load counts only the rows its mask sets. A TensorLoad takes them from its Execute line's tmask. A masked
  TensorLoadL2SCP takes them from the hart's last logged tensor_mask, or else counts all rows and says so in
  `masked_ops_rows_assumed_all`.
- Counts add up over every launch of one host run.

**The classes** are the energy manual's (`count_kernel.py classes` lists every mnemonic's):

| Class | Manual |
|---|---|
| `scalar_int` (compressed forms included; `compressed_instructions` counts them) | 03a Scalar integer, one cycle; Compressed |
| `int_muldiv` | 03a Scalar integer multiply and divide |
| `scalar_float`, `float_int_xfer` | 03a Scalar float; Between the float and integer register files |
| `vector_float`, `vector_int`, `transcendental`, `mask_broadcast` | 03a Vector float (the `fcvt.ps.*` conversions included), Vector integer, Transcendental, Masks and broadcasts |
| `load`, `store` | 03a Loads and stores that hit the L1 (the level they reached is section 4's question, below) |
| `load_past_l1`, `store_past_l1` | 03a Loads and stores that bypass the L1 (`fswl.ps` to the L2; `fswg.ps` by its address: the home slice, or a scratchpad) |
| `gather_scatter`, `gather_scatter_past_l1` | E48's gathers and scatters from the L1 (`fgw.ps`, `fg32w.ps`, ...); those that bypass it (`fgwl.ps`, `fgwg.ps`, `fscwl.ps`, `fscwg.ps`: 04 section 4.4, 27x or more the L1 form) |
| `branch_taken`, `branch_not_taken`, `jump` | 03a Branches and jumps |
| `atomic_local`, `atomic_global`, `atomic_packed`, `atomic_std` | 03a Atomics on a private line; 06 for shared lines |
| `tensor` (one per CSR write; the `tensor` block has the ops by format) | 03 section 3.2; 04 for the bytes |
| `cache_op`, `sync`, `system` | cache-control CSRs; fcc, fccnb, flb, stall; 03a System |
| `trap` | the thirteen instructions that trap in U-mode (and fcvt's 64-bit forms) |

**The profile route** (`count_kernel.py count --prof prof.txt.gz [--pc-offset auto|0x...|--pc-offset-from LOG.json]
[--assume-no-wait]`) rebuilds each instruction's count from the landings and their cycles by flow equations (the tool's
docstring). It is exact where they close, and it reports in `unresolved` where they do not.
- On sparse parity's working harts, the data-dependent loops with several exits leave 21-43% unresolved with default
  flags and 7-33% with `--assume-no-wait`. It never overcounted (`profile-route.json`).
- Its no-wait equation does not know the FP/vector stall. While thread 0's core has a tensor operation queued, sw-sysemu
  holds thread 0 at its next float or vector instruction (`insn_util.h` `require_fp_active`). A run holding one can take
  more cycles than instructions, so "lower bound" rests on the check against a log.
- `--pc-offset auto` scores every 4 KB-aligned candidate by the landing places it explains. The first version took the
  most-voted candidate and refused the scalar runs. Its tensor formats come from a constant the code loads
into the register it writes to `tensor_fma`, or from a log of the same kernel (`--tensor-map`). It is the route for a
run too big to log, read as a lower bound.

## Bytes by level: what the simulator can count, and what only the card can

**The simulator** (`sw-sysemu` `353f20e`) is functional: memory is storage, with no cache tags, no hit or miss and no
timing (`cache.h` maps the L1 scratchpad's lines; `memory/` holds dense and sparse regions). Every access in the log
carries its physical address and size, so the counter gives, per instruction class:

| Level | From the simulator | How |
|---|---|---|
| L1 data cache | the loads and stores that reach for it (`load`, `store`, vector `flw.ps`/`fsw.ps`): instructions and bytes | the class; hit or miss is unknown |
| L1 scratchpad | TensorLoads into it and their rows (64 B each); TenB loads | the tensor start lines |
| shire L2 / scratchpad | accesses past the L1 (`flwl.ps`, `fswl.ps`, `amo*l`), tensor loads and stores from and to scratchpad addresses, the own shire or another | the scratchpad region 0x00_8000_0000-0x00_FFFF_FFFF (`memmap.h`), shire field bits 23-29 (0x7F = own) |
| L3 (home slice), or a scratchpad | `*g` accesses (`flwg.ps`, `fswg.ps`, `amo*g`): instructions and bytes | the level follows the address: a DRAM address goes to its home L3 slice (whether the line was there is unknown), a scratchpad address to that shire's scratchpad (sparse parity's `fswg.ps` staging stores go to its own) |
| DRAM | accesses to DRAM addresses (cached, or the uncached alias with bit 38 set), tensor loads from DRAM, `TensorLoadL2SCP` copies | address 0x80_0000_0000 and up; which cache level served a cached access is unknown |
| mesh | accesses to another shire's scratchpad (`scratchpad_remote`) and to remote homes | the target shire is in the address; hops follow from the mesh map (`workloads/nocroute/meshmap.py`), not computed here |
| ESR / sync | accesses to the ESR region (barriers, credits) | address 0x01_0000_0000-0x01_FFFF_FFFF |

**Only the card's stock counters give the levels that served the traffic** (`docs/research/counters-and-dram.md`
sections 1-3 and 7; firmware `353f20e`), all readable from U-mode without new firmware:

- `hpmcounter3`: cycles (free-running; minion 0 of each neighbourhood; the late-carry correction `fixcyc`).
- `hpmcounter4`/`5`: retired instructions of thread 0 / thread 1, summed over the neighbourhood's 8 minions.
- `hpmcounter6`: L1 data-cache misses sent to the L2, summed over the 8 minions.
- `hpmcounter7`/`8`: the neighbourhood's instruction-cache requests and misses to the L2.
  (4-8 are zeroed before every launch; read them at the kernel's end; erratum 1.23: one hart of a minion at a time,
  the four-read `HPM_SAFE_READ` of et-common-libs' `pmu.h`.)
- System call 9 (`SYSCALL_PMC_SC_SAMPLE`, `a1` shire 0-32, `a2` bank 0-3, `a3` 1 = P0, 2 = P1, 0 = cycles): each
  shire-cache bank's read requests (P0: L2, L3-slave and scratchpad reads, hits and misses together) and write requests
  (P1), any shire. The firmware stops, reads and restarts the counter; the master minion samples the same counters, so
  take deltas.
- System call 10 (`SYSCALL_PMC_MS_SAMPLE`, `a1` memory shire 0-7, `a2` 1 = P0 reads, 2 = P1 writes, 0 = cycles at
  933 MHz): the DRAM side's mesh reads and writes. "One per 64 B line" is an assumption: the survey says P0 and P1
  count mesh reads and writes, not their size. Check it on the blind day against a known byte count (the copy's).

**The recipe for the blind day** (a desk recipe; the calls are the ones `workloads/nocroute/kernel/nocroute.c` and
`workloads/memprobe/kernel/memprobe.c` already make on the cards):

1. One hart of the whole launch (shire 0, minion 0, hart 0), after a barrier that every working hart of every shire
   has reached and before any of them starts (a chip-wide barrier: sparse parity's is per shire, so a kernel needs one
   such as `workloads/onchip`'s credit-release barrier, one atomic per shire and nobody polling, about 5,000 cycles), samples system call 9 for every shire 0-32, bank 0-3, P0 and P1 (264 calls), and
   system call 10 for every memory shire 0-7, P0 and P1 (16 calls). About 280 calls of a few hundred cycles each:
   well under a millisecond, so time the work between the barriers, not the sampling.
2. The work.
3. A second barrier; the same hart samples the same 280 counters again; the deltas are the launch's shire-cache
   read and write requests by shire and bank and its DRAM reads and writes by memory shire (x 64 B).
4. At its end, hart 0 of minion 0 of every neighbourhood reads `hpmcounter3`-`8` once (`HPM_SAFE_READ`, after its
   own hart 1 has finished: erratum 1.23) into its record: retired instructions by thread, L1 misses and
   instruction-cache misses, summed over the neighbourhood since the launch.
5. Beside them, the counter's run of the same kernel file on a small instance in the simulator: the instructions by
   class (which the card cannot give: its counters choose no events without firmware), each memory class's bytes by
   address region, the tensor ops by format. The card's L1 misses and shire-cache requests then split the
   simulator's L1-path bytes into L1 hits and the rest, and its memory-shire counts give the DRAM bytes; what the
   stock counters cannot split (L2 hits from L3 hits: both in P0) stays a bracket.
6. Compare the retired instructions per neighbourhood (`hpmcounter4`+`5`) with the counter's total for the same work.
   That is the check that the simulated instance and the card's ran the same code paths (spin loops aside: below).
   The card's counters count every privilege mode since the reset before the launch, the sampling ecalls included. The
   counter's `total` holds the kernel's U-mode work only. So add the same run's `outside_kernel.total.instructions`
   (about 1,560 firmware instructions a hart here) to the counter's side, or subtract it from the card's, and keep the
   sampling calls of steps 1 and 3 out of the window.

## Limits

- **Spin loops follow the simulator's timing.** A hart polling another hart's line (sparse parity's `wait_count`)
  executes as many polls as the simulator's timing gives, not the card's: on the L1 slices 0.04-81% of a hart's
  counted instructions were spin. Split them out by source line (as `card_compare_sparseparity.py` does with the `-g`
  build's addr2line) and take the card's own poll counts where the kernel reports them.
- **Timing-only fields vary between runs**: the kernel's cycle and wait records moved by up to 128 cycles (the
  `fixcyc` carry correction toggles with the launch's start cycle) and its wait cycles by a few hundred between runs
  of the same build; every count was identical.
- **A data-dependent kernel's counts are its instance's**: run the instance the card runs, or slices of it, and
  scale by what the kernel reports (ops, tiles), as `card_compare_sparseparity.py` does; its per-class fits left
  residuals up to 15% for the branches.
- **No cache model**: the levels that served cached accesses come from the card (above).
- The profile route needs the host built against the shadow prefix, and resolves only part of a data-dependent hart.
- A kernel ELF's sha256 differs by box: the two boxes' RISC-V GCC builds carry different version strings in `.comment`.
  Record a kernel by its `.text` and `.rodata` hashes (`objcopy -O binary -j .text`), not by the ELF's.

## Files

| File | What |
|---|---|
| `build_profiling_sysemu.sh` | builds the profiling simulator and its shadow prefix into a new folder (the options and why) |
| `run_counted.sh` | one host run in the simulator with the log streamed into the counter |
| `count_kernel.py` | the counter: `count` (log or profile), `table`, `compare`, `classes` |
| `test_count_kernel.py` | the counter's desk test on log lines in sw-sysemu `353f20e`'s exact formats (every tensor start line, a masked load, the firmware's work, a kill, a branch's direction changes) |
| `validate_sparseparity.py` | the counter against sparse parity's records (T1-T4, G1-G2, S1c), and the records against the host (S1) |
| `card_compare_sparseparity.py` | the L1 slices against the card's records and the cycle model, and the per-solve counts |

## Dated fixes (Thu 12 Nov 2026, Q166's fix lane, on its verifier's findings)

- **TensorStore lines crashed the log reader.** sw-sysemu prints TensorStore's and TensorStoreFromScp's `addr` and `stride`
  as `%016 PRIx64`, hex without `0x` (`insns/tensors.cpp` 1038, 1100), and the reader raised ValueError on them. A kernel
  that stores a tensor could not be counted. `addr` and `stride` are now always read as hex.
  - `test_count_kernel.py` feeds every tensor start line in its exact format, plus a masked load, the firmware's work, a
    kill and a branch's direction changes: 40 of 40 pass, on the Mac and on aifoundry3.
  - Two simulator runs of kernels that store tensors are in the data folder's `tensor-store/`. E101's GEMM kernel, gemm1
    in int8 on one shire (64 TensorStores, 65,536 B to DRAM, one per 32 ops), checks exact. The onchip probe's write
    launch (64 TensorStores, 32,768 B into the own scratchpad) was counted, but its host then aborted, with or without
    the log.
- **New fields:** `outside_kernel`, `by_csr`, `branch_direction_changes`, `branch_changes_per_pc`, masked loads by row,
  the class `gather_scatter_past_l1`, and `fcvt.ps.*` in `vector_float`.
- **Better behaviour:** the profile's automatic offset, and `--pc-offset-from`.
- **The validation runs were run again** with these tools, on the same binaries and arguments
  (`first-runs-regression.txt`). Every field of the first counts files reproduces exactly.

Standard library only (Python 3.8+). SPDX-License-Identifier: Apache-2.0
