# ET-SoC-1 prototyping notes

Condensed from the manuals in `external/et-man`, the micro-architecture docs in
`external/core-et/docs` (erbium branch), the et-platform sources, and the
FOSDEM 2026 talk "Zero to matmul with the ET-SoC-1". Section numbers like "PRM ch. 9"
point to the full details in `external/et-man/ET Programmer's Reference Manual.pdf`.

## The chip in one screen

| Level | Contents |
|---|---|
| **Minion** (core) | In-order RV64IMFC with Zicsr/Zifencei, **2 harts**. The 8-lane x 32-bit VPU widens `f0..f31` to 256 bits. It has one FMA, two integer multiply-accumulate (IMA), one integer and one transcendental unit. The **4 KB L1D$** is 16 sets x 4 ways x 64 B lines, shared/split per hart, or partly an L1 scratchpad. The L1D$ is **not coherent**. |
| **Neighborhood** | 8 minions sharing a 32 KB L1 I$, plus an L0 micro-I$ per 4 minions. Cooperative tensor loads coalesce identical requests. |
| **Shire** | 4 neighborhoods = **32 minions / 64 harts**. **4 MB SRAM**, split between L2 cache, L3 slice, and L2 scratchpad (L2Scp). The typical split is 512 KB L2, 1 MB L3, 2.5 MB scratchpad. There is also an uncacheable block with fast local barriers (FLB), fast credit counters (FCC), IPIs, and global atomics. |
| **Chip** | 34 minion shires (32 compute + master + spare) = 1088 minions. There are 4 out-of-order Maxions, 1 service processor (SP), and a mesh NoC. DRAM is 16 x 16-bit LPDDR4X channels (~133 GB/s peak, up to 32 GB; the V3 dev card has 32 GB), and the host link is PCIe Gen4 x8. |

Software sees **2048 harts** on the 32 compute shires (`hartid = shire*64 + minion*2 + thread`).
The FOSDEM talk measured about 10.25 TFLOP/s fp32 on 1024 minions at 650 MHz. The theoretical peak there is 1024 x 8 lanes x 2 flop x 0.65 GHz = 10.6 TFLOP/s.

## Software stack (et-platform, installed to `/opt/et`)

- **Host:** `runtime` (esperanto-tools-libs) → `deviceLayer` → either the `et-driver` kernel module
  (real card: `/dev/et*_ops`, `/dev/et*_mgmt`) or **`sys_emu`** (sw-sysemu, the simulator).
  The API is CUDA-like: `mallocDevice`, `memcpyHostToDevice`, `kernelLaunch(stream, kernel, args, shireMask)`,
  and `waitForStream`. Kernels are RISC-V ELFs that get relocated at load time.
- **Device firmware:** SP bootloaders (`device-bootloaders`), then the master-minion runtime and the
  worker-minion runtime (`device-minion-runtime`). User kernels run in **U-mode** on the worker shires.
- **gp-sdk** is the "write your own kernel" layer that this repo builds on:
  - Device: `DECLARE_KERNEL_ENTRY_POINTS(entry_hart0, entry_hart1)`. Pass `nullptr` for hart 1 to use one hart per
    minion. The device-side helpers are `get_relative_thread_id()`, `get_num_threads()`, `get_shire_mask()`, and
    `et_printf()`, which writes to the trace buffer.
    Headers live under `et-common-libs/include/etsoc/isa/*.h`: hart ids, cacheops, atomics, FLB/FCC barriers, and tensors.
  - Host: `GenericLauncher` does init/load/launch/wait/trace-dump. `--device_type=sysemu|silicon`
    selects the simulator or the PCIe card, so **the same binary runs on both**.
- The compiler is `riscv64-unknown-elf-gcc` 15.2 from `aifoundry-org/riscv-gnu-toolchain` (branch `et`), with
  `-march=rv64imfc -mabi=lp64f -mcmodel=medany`. The ET instructions (`flw.ps`, `fmadd.ps`, `fbcx.ps`, ...) assemble
  without extra flags. There is **no hardware fdiv/fsqrt**: `-mno-fdiv` is set, and gp-sdk's `etgcc`/`etm` provide replacements.

## Memory model: the main trap

The chip has up to about 2465 caches and **no coherency between them**. L1D$ lines are 64 B and get written back
whole, so two harts on different minions that write to the same line will clobber each other. On FOSDEM slide 14,
parallelizing the inner matmul loop gives wrong results for exactly this reason.

Options, cheapest first:
1. **Give each hart whole 64 B lines** of any output. The saxpy example rounds work per hart up to 16 floats,
   and `kernels/hello` uses one line per hart. The firmware evicts L1 after the kernel returns.
2. **Use "L" / "G" memory ops** (PRM ch. 5 and 7):
   - `…L` ops (`fswl.ps`, `flwl.ps`, `sbl`, `shl`, `amo*l.{w,d}`) go straight to the local shire's L2.
   - `…G` ops (`fswg.ps`, `flwg.ps`, `sbg`, `shg`, `amo*g.{w,d}`) go to the address's home cache. They are
     coherent-looking but slower.
3. **Explicit cache ops** (PRM ch. 8): U-mode `EvictVA` / `FlushVA` / `PrefetchVA` CSRs. Before a cacheop, `fence`.
   After a cacheop and before touching the same lines, `tensor_wait`.
4. Use **barriers**: FLB (`flb` CSR, per-shire fast local barrier) and FCC credit counters (PRM ch. 10–11).
   `gp-sdk/device/sdk/include/sync.h` and `flbLock.h` wrap these.

## Performance ladder (FOSDEM "Zero to matmul", 512x512 fp32)

| Step | Result |
|---|---|
| Naive scalar, 1 hart | 7 MFLOP/s |
| Parallelize over `mhartid`, 512 harts. Fix the output race with `L` stores. | 3.4 GFLOP/s |
| Use all 2048 harts | 13.1 GFLOP/s |
| 8-lane SIMD (`fbc.ps` broadcast A, `flw.ps` load B, `fmadd.ps`) | 104 GFLOP/s |
| Put A and B in **L2 scratchpad** instead of DRAM | 312 GFLOP/s |
| Register-block 2x16 outputs per hart. FMA share goes from 14% to 32%. | 1.64 TFLOP/s |
| Register-block 4x32. FMA share is 63%. | 2.94 TFLOP/s |
| **Tensor unit**: `tensor_load` A into L1Scp and B streamed, then `tensor_fma` (16x16 fp32), `tensor_store`. Hart 0 only. | 7.05 TFLOP/s |
| Software-pipeline: overlap the next A-load with the current FMA, double-buffering L1Scp | **10.25 TFLOP/s** |

Why the tensor step helps: the front end issues only one RISC-V instruction per cycle, and the two harts share it.
The tensor load and compute engines take a single CSR write (`csrw tensor_fma`, …) that enqueues up to 512 ops or 1 KiB
of loads. These then run asynchronously, so the core can exceed 1 IPC.

Other ideas the talk left on the table:
- Have hart 1 stream data into L2Scp with `TensorLoadL2Scp` (it is allowed on hart 1).
- Use cooperative tensor loads across a neighborhood.
- Use fp16 (`TensorFMA16A32`) and int8 (`TensorIMA8A32`) variants for 2x and 4x the K-depth per op.

## Tensor extension in brief (PRM ch. 9)

- Instructions are CSR writes: `tensor_load`, `tensor_load_l2scp`, `tensor_fma`, `tensor_quant`, `tensor_store`,
  `tensor_reduce`/`recv`/`broadcast`, and `tensor_wait`. The stride goes in `x31`. The configuration CSRs are
  `tensor_mask` (0x805), `tensor_conv_size`/`tensor_conv_ctrl`, `tensor_coop`, and `tensor_error` (0x808).
- An FMA computes `C[M][N] += A[M][K] * B[K][N]` with M,N ≤ 16 and K ≤ 64/sizeof(elem). A comes from the L1 scratchpad,
  which is carved out of the L1D$ (48 lines of 64 B). B streams through TenB. C accumulates into hart 0's vector registers.
  Element types are fp32, fp16→fp32, and int8→int32 (via TenC).
- Tensor ops do not follow program order. You synchronize with `tensor_wait <id>`.
  Only hart 0 may issue tensor ops, except `TensorLoadL2Scp`, `TensorWait`, and `tensor_coop`.
- `gp-sdk/device/tests/txfma` and `autogenMatmul`, and `dnn-library`, are the in-tree examples to crib from.

## A0 silicon errata that matter for kernels (`external/et-man/ET-SoC Errata.pdf`)

- **1.29 VPURF timing path.** A VPU register read in the cycle after a write can return stale data.
  The fixes depend on instruction type:
  - Loads and transcendentals (Type A): force the dependency with `fmv.x.w x0, fN`, then put one more instruction before the consumer.
  - Integer, move, and FP compute (Types B and C): need ≥8 independent instructions, a taken branch, or a forcing sequence.
  - Tensor ops (Types D–G): have their own rules.

  The FOSDEM matmul inner loop contains an "useless" `fsgnjx.s f3,f1,f2` for this reason.
  **The gcc 15.2 in this setup does not insert these workarounds.** Evidence from 2026-09-18:
  - Running gp-sdk's `saxpy_vector.elf` with `--simulator_params="-vpurf_warn"` flags "VPURF workaround required for type A" on every compute shire.
  - The flagged sequence is the inner loop `flw.ps fa5 → fmadd.ps fa5,… → fsw.ps fa5`.
  - Some firmware routines on the SP and master shire are flagged too.

  Results in the simulator are still correct because `sys_emu` does not model the bug.
  On silicon (aifoundry3, 2026-09-18), `workloads/sgemm` has the flagged `flw` → `fmadd.s` pattern on essentially every FMA
  (GCC 15.1 there), yet it produced correct results for all 1.6 M checked outputs. So the hazard is at least not easy to hit.
  Still, check kernels with `-vpurf_warn` / `-vpurf_check`. Treat wrong-results-only-on-silicon as a prime suspect for this bug,
  and ask AI Foundry whether the lab cards are A0 and whether the compiler is meant to handle it.
- Also relevant:
  - 1.3: gather/scatter can drop ops on context switch.
  - 1.8: the mask is ignored for contiguous vector stores that bypass L1.
  - 1.15/1.16: misaligned accesses.
  - 1.21: implicit `x31` dependency of `amocmpswap`.
  - 1.26: tensor mask leaking between threads for cacheops.
  - 1.28: UC-op starvation between harts.

## Simulator (`sys_emu`) tips

- `sys_emu` is **functional, not cycle-accurate**. Use it for correctness and debugging. Measure performance on silicon.
  It is also slow: booting the firmware and running 2048 harts takes a while, so iterate on a small `--shire_mask` first.
- When `sys_emu` is started through the runtime (the launchers and `it_test_*`), these checkers are **on by default**:
  `mem_check`, `l1_scp_check`, `l2_scp_check`, `flb_check`, and `tstore_check`. DRAM also resets to `0xDEADBEEF`.
  The VPURF checker is off by default.
- Useful flags (via the launcher: `--simulator_params="…"`, or `make run-hello SIM_PARAMS="…"`):
  - `-vpurf_check` / `-vpurf_warn`: errata 1.29 hazards.
  - `-mem_check`: L1 coherency violations, i.e. the section above.
  - `-l1_scp_check`, `-l2_scp_check`, `-flb_check`, `-tstore_check`.
  - `-gdb` / `-gdb_at_pc <pc>` / `-gdb_on_umode`: gdb stub. Use `riscv64-unknown-elf-gdb` with the `*.elf_dbg` kernel.
  - `-l`, `-lm <minion>`, `-lt <thread>`: instruction trace. Also `-max_cycles`, `-dump_prof <file>`, `-mem_reset`.
- Standalone bare-metal ELFs run directly with `sys_emu -elf foo.elf -minions 0x1 -shires 0x1 -single_thread -l`
  (see `sw-sysemu/examples/`). This is handy for ISA micro-experiments without the runtime.
- Device `et_printf` output goes to the trace buffer, not stdout. The launcher dumps it to `traceKernels_dev0_<i>.bin`
  in the run dir. Esperanto's `dt2json` decoder is not open source, so use `build/launchers/trace_dump <file>`
  (or `make trace`) instead.
- Simulated boot takes about 37 s before the first kernel launch: SP BL2, then master/machine/worker minion firmware
  on 33 shires. The whole hello run is about 40 s.

## Where to read more

| Topic | Document |
|---|---|
| ISA extensions, CSRs, memory map | PRM ch. 3–9 (SIMD, PS/PI ops, atomics, cacheops, tensor), ch. 15 (memory map, scratchpad layout) |
| Minion pipeline, VPU latencies | `core-et/docs/Minion Description.pdf`, `Minion VPU Specification.pdf`, `FE-Intpipe-Description.pdf` |
| L1D$ modes, L1Scp | `core-et/docs/Minion DCache Description.pdf` |
| Shire cache (L2/L3/Scp) | `core-et/docs/CORE-ET-Shire-Cache-Specification.pdf` |
| Tensor loads across a neighborhood | `core-et/docs/Cooperative-TensorLoad-Description.pdf`, `CORE-ET-Neigborhood-MAS.pdf` |
| Board | `et-man/ET-PCIe-Dev-Card-V3.pdf`, `ET Preliminary Datasheet Rev 1.0.pdf` |
| Example kernels | `et-platform/gp-sdk/device/tests/*`, `et-platform/dnn-library`, `aifoundry-org/llama.cpp` (ET port) |

Note that core-et's `erbium` branch is the RTL for **Erbium**, a new MCU-class SoC with one 8-minion neighborhood. Its
docs describe the same Minion core and are the best micro-architecture reference. et-platform can also build
"erbium-soc1sim" kernels (Erbium-style kernels running on ET-SoC-1) via `add_erbium_riscv_executable()` in gp-sdk.
