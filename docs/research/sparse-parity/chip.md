# The ET-SoC-1 for a sparse-parity solver: what it offers and what it costs

Brief SP2, 28 September 2026, from the repository and manuals (no card access). **M** measured, **R** read from a
manual or source, **D** derived here. `PRM` is `external/et-man/txt/ET Programmer's Reference Manual.txt` and `EM`
is `docs/energy-manual/` (`external/` is gitignored).

## 1. Planning figures

| | Value | Kind, source |
|---|---|---|
| Kernel cores | 32 shires x 32 minions = 1,024 minions, 2,048 harts; `hartid = shire*64 + minion*2 + thread` (of 34 shires, one is the firmware's master and one a spare) | R, `docs/et-soc1-notes.md:20-22` |
| Clock | 600 MHz on a warm die (above 65 °C, the usual state); of the cards in use only aifoundry2 reaches 800 MHz, when cool | M, `docs/et-soc1-notes.md:251-257` |
| Issue | One instruction per minion-cycle, shared by its 2 harts; measured 0.37 per hart (0.74 per minion) for 1-cycle scalar and `.pi` ops. Tensor ops run asynchronously | R, `docs/et-soc1-notes.md:297-299`; M, `EM/03a-every-instruction.md:14-34,125-151` |
| int8 tensor peak | 128 OP per minion-cycle: 2.46 / 3.28 TOP/s per shire and 78.6 / 105 per chip (600 / 800 MHz). Measured **71.8 TOP/s** (280 cycles per op, B through TenB) and 63 TOP/s (318 cycles, B in L1Scp) | D; M, `docs/et-soc1-notes.md:319-325`, `EM/03-instructions.md:120-122` |
| fp32 / fp16 tensor peak | 16 / 32 FLOP per minion-cycle: chip 9.83 / 19.7 TFLOP/s at 600 MHz and 13.1 / 26.2 at 800. Measured 9.51 / 19.0 | D; M, `docs/findings/05-claims.md:446` |
| Vector bit ops | 256 per `fxor.pi`: 157 T/s per chip at 1 IPC, 600 MHz; 116 T/s at 0.74 | D |

## 2. ISA for bit work

- **Base:** RV64IMFC + Zicsr + Zifencei (`external/et-man/txt/ET Minion Overview.txt:2`), built with `-march=rv64imfc`
  (`/opt/et/lib/cmake/riscv64-ec-toolchain.cmake:33`).
- **No bit-manipulation extension** (no Zbb, `cpop`, `clz`, `clmul`): `external/et-platform/sw-sysemu/insns/` has
  only base, M, F, C, packed, tensor and CSR files. `__builtin_popcountll` becomes libgcc's `__popcountdi2`, 12 SWAR
  ops with one 64-bit `mul` (disassembly of `build/sgemm/kernel/sgemm.elf`, from `workloads/sgemm/kernel/sgemm.c:25`);
  `mul` issues at 1/8 rate, 43 pJ (`EM/03a-every-instruction.md:47`), so a shift-add fold (about 17 one-cycle ops)
  avoids it.
- **Vector unit:** 8 lanes x 32 bits; each hart's `f0-f31` is 256 bits wide (1 KB). The `.pi` logic ops, shifts,
  adds and **`fmul.pi` all issue at the full rate** (`EM/03a-every-instruction.md:125-151`), so a 256-bit SWAR
  popcount is about 12 `.pi` ops (21 bits per instruction, against 4-5 for scalar code), and about 6 with Harley-Seal
  carry-save accumulation (D).
- **Masks:** 8 registers of 8 bits, a bit per lane (`PRM:1284-1286`); `fsetm.pi` marks nonzero lanes (`PRM:2920`),
  `maskpopc` counts them, `mova.m.x`/`mova.x.m` move all 64 bits (`PRM:1378-1410`; `external/et-platform/sw-sysemu/insns/packed_mask.cpp:54-130`).
  A cheap "any lane nonzero?" test; not a faster 64-bit popcount (16 ops).
- **Branches:** taken 0.058 per hart per cycle (24 pJ), data-dependent 0.1-0.12 (`EM/03a-every-instruction.md:203-208`):
  batch early exits.

## 3. Tensor unit (PRM ch. 9)

- `TensorIMA8A32` computes `C[16x16] int32 += A[16x64] x B[64x16]`, with each int8 operand signed or unsigned (the
  UA/UB bits). The sums are exact 32-bit and accumulate in TenC; bit 23 copies C to `f0-f31` (`PRM:7677-7760`). The
  fp32 op is 16x16x16 and the fp16 op 16x16x32.
- A sits in the L1 scratchpad: 48 lines, 3 KB, which only hart 0's tensor ops can use (`PRM:5999-6002`). B sits in
  the L1 scratchpad or streams through TenB. `TensorLoadInterleave8` lays B out for int8 (`PRM:7103-7115`).
- **Only hart 0 may issue tensor ops**, except `TensorLoadL2Scp`, `TensorWait` and `tensor_coop` (`PRM:6550-6552`),
  so hart 1 is free for scalar or vector work.
- Zeros save energy, not time (318 cycles per int8 op at any sparsity; `docs/et-soc1-notes.md:148-157`).
- Errata 1.29, which GCC ignores: `fmv.x.w x0, fN` after a tensor op writes `f` registers, and 8 instructions or a
  taken branch between a vector write and its read (`docs/et-soc1-notes.md:343-360`; `workloads/sparsity/kernel/sparsity.c:41-54`).

## 4. Memory

| Level | Size | Latency (cycles) | Bandwidth at 600 MHz | pJ/B |
|---|---|---|---|---|
| L1D (the firmware's mode) | **512 B per hart** plus 3 KB L1Scp | 5 | 6.2 TB/s per chip, about 10 B per minion-cycle | 0.75 |
| L2 / own L2 scratchpad | 512 KB / **2.5 MB per shire** (80 MB per chip) | 47 | 128 B per shire-cycle, 2.46 TB/s per chip | 3.1 / 2.3-4.4 |
| Remote scratchpad / L3 | 32 MB of L3 per chip | 112-220 / 159-169 | 0.96-0.98 TB/s | 5.1-11.8 / 14.7 |
| DRAM | 32 GB | about 290 | 76 GB/s | 115 |

M, `docs/et-soc1-notes.md:70-77,90-96`; energies above idle. Firmware resets the L1 mode every launch
(`external/et-platform/device-minion-runtime/src/MachineMinion/src/syscall.c:348-385`). Scratchpad address
`0x80000000 + (shire<<23) + offset`; offset 0 faults, start 256 KB in (`docs/findings/14-card-behaviour.md:402`).
Host to card: 12.5 GB/s DMA, 5-8 GB/s staged (`docs/findings/05-claims.md:546-548`).

## 5. Energy per operation (600 MHz, above idle, random operands)

| Operation | pJ | Source |
|---|---|---|
| `xor`, `and`, `add` (64-bit) | 9.6 (6.0 on zeros); `nop` 5.4 | `EM/03a-every-instruction.md:14-41` |
| `fxor.pi`, `fand.pi`, `fsrli.pi`, `fmul.pi` | 20.5, 19.7, 16.0, 50.0 (`fxor.pi` is **0.08 pJ per bit**) | `:125-148` |
| `ld`, `flw.ps` (L1 hit) | 11.6, 17.1 | `:176-190` |
| int8 MAC (zeros / ones / randn) | 0.060 / 0.118 / **0.295**; 1.47 including idle | `EM/03-instructions.md:120-122` |
| Byte between cores | 0.69 within a pair, 2.2 within a shire, about 9 + 1.75 per hop across the mesh | `EM/05-bytes-between-cores.md:9-19,31` |
| Idle card | 35.9 W at 80 °C (aifoundry2), +0.65 W/°C; aifoundry1 card 1 about 10 W higher | `EM/01-at-rest.md:9,12` |

Static power dominates. Idle power is about 1 pJ per int8 MAC at the chip's rate, and 0.3 pJ per vector bit-op
(D). A dense matmul spends 57% of its energy on it (`EM/07-composition.md:30`). The idle cost is the same whether 1
shire or 32 are busy, so **using all 1,024 minions cuts energy per solve**, not only time.

## 6. Launch and synchronisation

- **Launch:** empty kernel on 32 shires 556-566 µs launched and waited, 104 µs each queued (M,
  `docs/findings/05-claims.md:550-551`); device open about 0.19 s (`workloads/sgemm/README.md:69`).
- **Shire:** FLB + credit barrier 233 cycles; TensorReduce + broadcast over 32 minions 444 cycles, with free integer
  add/max combine (M, `EM/06-synchronisation.md:47-48`, `docs/et-soc1-notes.md:124-127`).
- **Chip:** 1,024-minion reduce 1,393 cycles (2.3 µs); atomics + credits barrier 5,007 cycles (8.3 µs); a contended
  global atomic 10 cycles per op, 19.8 nJ (M, `EM/06-synchronisation.md:43-46`; `docs/reports/2026-09-18-et-soc1-sparsity.html:883`).
- **So (D):** a solve needs at least about 50 ms of kernel time for the launch to cost under 1%. Batch small
  instances per launch.

## 7. Traps

The L1 is not coherent: each hart writes only its own 64 B lines (`docs/et-soc1-notes.md:46-60`). U-mode has no
divide, square root, `fcvt.s.l[u]` or `double`, and the `cycle` CSR traps (`docs/findings/14-card-behaviour.md:396-401`).
Tensor ops are hart 0 only (`:412`). Never spin on a global atomic (`:405`), and never receive `TensorSend` from two
partners at once, which hangs the card (`:413-418`). `hpmcounter3` can read 128 short (`fixcyc()`,
`workloads/memprobe/kernel/memprobe.c:26-40`).

## 8. Templates: split, launch, time, build

- **Split:** shire mask and minions per shire are kernel arguments. `sgemm` numbers harts
  `popcount(mask below shire)*64 + (hart&63)`, grid-stride over 64 B units (`workloads/sgemm/kernel/sgemm.c:18-35`);
  `sparsity` takes `--shires MASK --per-shire N` and returns hart 1 in tensor modes
  (`workloads/sparsity/kernel/sparsity.c:550-563`; sweeps 1 minion to `0xFFFFFFFF` x 32, `workloads/sparsity/run_lab.sh:18-19`); a
  timed-out shire barrier is `sparsity.c:120-141`.
- **Host** (runtime API, no gp-sdk): `registerRuntimeLogLevels()` first, then `IRuntime::create`, `loadCode`,
  `mallocDevice`, `memcpyHostToDevice`, `setShireMask/setBarrier`, `kernelLaunch`, `waitForStream(timeout)`,
  `--budget 8` (`workloads/sgemm/host/main.cpp:86,156-209`); `--sysemu` checks correctness only. Per-hart result
  records carry `hpmcounter3` at entry and exit (`sparsity.c:590-599`).
- **Build:** `kernel/{crt.S,sections.ld,*.c}` + `host/main.cpp`, `add_riscv_executable` with `et-common-libs::cm-umode`
  (`workloads/sgemm/kernel/CMakeLists.txt`); `cmake -S workloads/sparseparity -B build/sparseparity -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && nice cmake --build build/sparseparity -j4`.
  `scripts/deploy-lab.sh <host> <dir>` builds in `~/nekko` (`:26-35`); not where a queue runs, and never into a
  campaign's build directory (`AGENT.md:203-215`).
- **Run (with the owner's card time only):** `et-who`, then
  `flock -n /run/lock/etsoc-shire0.lock timeout 10 build/sparseparity/host/sparseparity_host ...`; on aifoundry1
  `ET_DEVICES=1` and the shire1 lock (`AGENT.md:162,232-240`).

## 9. What this means for sparse parity (D)

- **Split:** each hart takes a rank range of k-subsets; then one shire reduce (444 cycles) and a host pick.
- **Bit-sliced:** the first 32 samples of 256 columns fit in a hart's `f0-f31`. A noiseless early-exit test
  (`flw.ps`, `fxor.pi`, `fsetm.pi`, branch on `maskpopc`) is about 4 instructions per 8 candidates: 6-9e11
  candidates/s per chip, the low end when columns stream from L2 (4 B per minion-cycle). Noisy labels need a full
  popcount, about 7 `.pi` ops per 256 samples per candidate.
- **Tensor correlation:** with ±1 or 0/1 bytes, k=2 correlations are `X^T diag(y) X` (k=3: pair-product rows), at
  3.2-3.6e13 exact MACs/s and 0.1-0.3 pJ per MAC marginal; hart 0 issues about 1 instruction per 280 cycles.
- **Where 1,000 cores show:** at 1e10 or more instructions (20 ms or more at about 4.5e11 per second per chip), for
  example noiseless n=1000, k=4 (4e10 candidates) or noisy n=300, k=4, m=1024. Below that the launch dominates.
- **Caution:** GF(2) elimination solves noiseless parity in n³/64 word operations (milliseconds on one host core at
  n=1000), so the chip matters for noisy (LPN-like) instances or a constrained learning rule.
