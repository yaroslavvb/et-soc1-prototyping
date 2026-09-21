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

## Memory hierarchy, measured (aifoundry2, 2026-09-18)

Measured with `workloads/memhier`. The full write-up, including the A100 comparison, is
`docs/reports/2026-09-18-et-soc1-memory-hierarchy.html`. Latencies are load-to-use, one dependent chain.

| Level | Size | Latency | Chip bandwidth | Energy (card, above idle) |
|---|---|---|---|---|
| L1 data cache | **512 B per hart** (firmware sets scratchpad mode) | 5.25 cycles | 7.6 TB/s | 1.8 pJ/B |
| L2 read buffer | 8 lines x 4 banks = 2 KB | 36 cycles | – | – |
| L2 | 512 KB per shire, private | 47 cycles | 2.8 TB/s | 4.3 pJ/B |
| L2 scratchpad | 2.5 MB per shire | 47 local; 112–271 remote | 2.6 / 1.0 TB/s | 2.8 / 6.3 pJ/B |
| L3 | 1 MB per shire, 32 MB shared | 169 cycles, ~280 ns | 1.0 TB/s | 10.8 pJ/B |
| DRAM | 32 GB LPDDR4X | ~440 ns (421–486) | 76 GB/s | ~150 pJ/B |

What this means for kernels:
- **Plan on 512 B of L1 per hart.** Before every launch the firmware (`init_l1`) sets D1Split and SCPEnable. That
  gives hart 0 sets 12–13 and hart 1 sets 14–15, and sets 0–11 become the 3 KB tensor scratchpad (PRM table 8.4).
  Hart 1 also pays +3 cycles on every L1 miss.
- **Stage shared data in the L2 scratchpad.** It is as fast as L2 (47 cycles), it is L1-cacheable, and it costs a third
  less energy per byte. Format 0 addressing: `0x80000000 + (shire << 23) + offset`, where shire `0x7F` means the
  local shire. Only the master shire's scratchpad is used by the firmware.
- **Remote shires cost 12–16 cycles per mesh hop**, and latency is not symmetric between shire pairs.
- **Count on the clock varying.** The card runs a "managed power" DVFS governor (65 W TDP) that moves the minion clock
  between 600 and ~850 MHz under load. On-chip latencies are fixed in cycles; L3 and DRAM latencies are fixed in ns.
  Time with wall clock as well as `hpmcounter3`.
- **Avoid concurrent PMU reads.** When both harts read `hpmcounter3` at once, one can get a wrong value (erratum 1.23).

## On-chip communication, measured (aifoundry2, 2026-09-18)

Measured with `workloads/nocbench` at 600 MHz. The full write-up, including the GPU comparison, is
`docs/reports/2026-09-18-et-soc1-on-chip-communication.html`.

The 32 compute shires sit on a 6x6 mesh, laid out as in marty1885's map (`MARTY` in `workloads/nocbench/analyze.py`).
Between shires, every latency is a + b x (Manhattan distance on that map), and each hop costs 20 ns round trip
(12 cycles at 600 MHz). A ring that visits all 32 shires one hop at a time:
0 24 9 25 2 11 19 27 18 10 17 14 22 26 15 23 31 7 6 30 29 5 28 20 12 21 13 1 16 4 3 8.

| Primitive | Round trip or cost | Notes |
|---|---|---|
| TensorSend/Recv, 32 B | 68 cycles on a tree edge; 114 elsewhere in the shire; 150 + 12/hop between shires | Tree edges in each neighbourhood: 0-1, 0-2, 0-4, 2-3, 4-5, 4-6, 6-7 (the fast local network). Each extra 32 B register costs 2.3-4.6 cycles. |
| Combine on receive (FADD/FMAX/IADD/IMAX) | +0 cycles | |
| TensorReduce + TensorBroadcast | 432 cycles for 32 minions; 1,368 for 1,024 | All 32 shires can reduce in parallel with no slowdown. |
| Credits (CREDINC store + FCC wait) | 120 cycles in a shire (blocking); 148 + 12/hop across shires (polled) | |
| FLB + credit barrier, 32 minions | 237 cycles | |
| Chip barrier from global atomics + credits | ~5,000 cycles | The allreduce tree is 3.7x faster. |
| Flag through global atomics (GPU-style) | 355-690 cycles | Depends on where the flag's L3 line lives, not on distance. |
| Aggregate bandwidth, 1 KB messages | 3.0 TB/s on tree-edge pairs; 1.1 TB/s in shire rings; 0.09-0.16 TB/s across the mesh | TensorLoad from a remote scratchpad does 0.98 TB/s. |
| Energy per byte | 0.8 pJ on tree edges, 2.3 in a shire, ~10 + 1.9/hop across the mesh | Card power above local idle. |

Rules for kernels that talk:
- **Never let a minion receive readies from two TensorSend partners at once.** The hardware keeps one peer-to-peer ready
  bit per minion (`partner_ready_peer` in core-et `dcache_reduce.v`), not one per partner. Change partners only across a
  barrier. Rings are safe, because a minion only ever sends to its `next`. Tree ops keep one bit per level and are safe.
  `sys_emu` tracks every partner separately, so it will not catch this. On silicon it hangs the hart for good, the
  firmware's abort cannot recover it, and the card then needs a reset. The lab admin asks to be pinged to power-cycle it.
- **A blocked FCC wait cannot be interrupted either.** When credits cross shires, poll `fccnb` (CSR 0xCC0) with a bailout
  before the blocking `csrw fcc`.
- **Keep bulk traffic inside shires, or pull it with TensorLoad.** Messages are for small, latency-critical exchanges and
  for in-network combines.

## Sparsity, measured (aifoundry3, 2026-09-18)

Measured with `workloads/sparsity` at a steady 600 MHz. The full write-up is `docs/reports/2026-09-18-et-soc1-sparsity.html`.

| Hook | Time | Energy |
|---|---|---|
| TensorFMA zero-skip (PRM 9.4) | None. 546 cycles per 16x16x16 fp32 op at 0-100% zeros in A or B, scattered, by column or by row. fp16 546, int8 318, any sparsity. | Yes, in a TensorFMA-only loop. Board power above idle scales with nonzero multiplies: 2.4 W + 14.8 W x fraction (1,024 minions). A gated slot costs ~0.5 pJ, an active one ~3.8 pJ. In the batch-1 layer below, where loads dominate, 90% zeros alone save only ~12% of power above idle. |
| fp16 zero-skip | The PRM rule (skip unless all four operands are nonzero) is a doc bug. Silicon computes the correct sum. | |
| `tensor_mask` on TensorFMA | None: 544-546 cycles with 0-16 rows enabled. | Masked rows are gated like zeros. |
| `tensor_mask` on TensorLoad | From L2 or scratchpad, time scales with the rows loaded down to a ~45-cycle floor (160 -> 81 -> 45 cycles for 16/8/4 rows). From DRAM on one minion, nearly in proportion (730 -> 320 -> 144 -> 73 cycles for 16/8/4/1 rows; a lone minion issues about one line per 45 cycles). From DRAM with the whole chip streaming: no gain. | |

Rules for sparse kernels:
- **Get speed from fewer or smaller ops, not from zeros.** Skip all-zero tiles, shrink AROWS/ACOLS, and mask loads.
  The tensor unit's gating only saves energy.
- **Keep weights you want to skip in SRAM.** Masked loads save no time once the whole chip saturates DRAM.
- A batch-1 1024x4096 fp32 layer with W in the scratchpads (all 1,024 minions, TensorReduce inside each shire) takes
  7.5 us dense (7.3 us with plain loads) and 2.1 us at 99% zero activations. The gains past ~50% zeros come from skipping
  whole 16-element slices.
- 8-lane SIMD with lane refill keeps 46-96% of lanes busy on heavy-tailed work (a 32-lane warp: 8-35%), but a simple
  vector-FMA loop reaches only ~1.5 lane-FMAs per cycle per minion, so divergence alone does not beat a modelled A100.
- `sys_emu -vpurf_check` aborts on the firmware's own code; use `-vpurf_warn` and filter for the kernel's PCs.
  A TensorStore read back by another minion's TensorLoad needs the shire's coalescing buffers drained first.

## One memory access, taken apart (aifoundry2, 2026-09-19)

Measured with `workloads/memprobe`. The full write-up is `docs/reports/2026-09-19-et-soc1-memory-anatomy.html`.
Cycles at 600 MHz, load-to-use, one load at a time.

| Stage | Cost | How it was found |
|---|---|---|
| L1 hit / L2 hit | 5 / 48 cycles (37 from the bank's read buffer) | `evict_va` the line to a level, time one load |
| L3 hit | 110 + 12 x hops(requester, home shire); home = PA[10:6] | 1,500 lines, all within ±2 cycles but 2 |
| DRAM leg past L3 | 91 + 12 x hops(home shire, memory shire); memory shire = PA[8:6] | memory shires 0-3 sit one step off the north edge at x = 1-4, 4-7 off the south edge; syscall 10's read counters confirm PA[8:6] |
| Row state | open-row hit saves 11 cycles (tRCD); same bank, other row: +40 cycles; rows = PA[18+], bank PA[12:10], column PA[17:13] | two back-to-back loads, one address bit flipped |
| Refresh | every 2,325 cycles = 3.88 us; a load caught in it waits up to 210 cycles; it closes the open row | 19,000 DRAM loads at random phases |
| Energy per 64 B load (above idle) | L1 46 pJ, L2 183, L3 local 541, +59 per hop, DRAM 5.1 nJ (67% DDR side, 18% mesh) | 1,024 minions; minion/SRAM/NoC rails from the service processor's stats trace |

Things to know when measuring:
- **`hpmcounter3` reads 128 short when its low 7 bits are 0-10.** The carry into bit 7 lands 11 cycles late: the PMU's 12
  counters share one adder that folds 7-bit pre-counter overflows into the post-counters round-robin, and reads ignore the
  pending overflow (`rtl-sim/pmu_carry` reproduces it from the original RTL). Add 128
  (`fixcyc()` in `workloads/memprobe/kernel/memprobe.c`); the firmware's four-reads workaround does not fix it. The
  `cycle` CSR traps in U-mode.
- **`evict_va` is asynchronous.** Fence and wait a few hundred cycles before timing. Level codes name where the line is
  left (1 L2, 2 L3, 3 memory; 0 does nothing). Evicts from many minions serialize in the shire cache.
- **Rail power:** `dev_mngt_service -n 0 -t SPST:extract` gives minion, SRAM and NoC rail power (a moving average,
  one record per 133 ms) plus board power. The ring holds ~15 minutes, and an extract returns only records since the
  last wrap. No rail covers the memory shires or DRAM.

## Power and temperature, measured (aifoundry2, 2026-09-20)

Full write-ups: `docs/reports/2026-09-20-et-soc1-power-temperature.html`, `docs/reports/2026-09-20-horace-experiment.html`.

- **Power depends on temperature:** +0.78 W per °C on the board at constant work (0.38 on the minion rail). The die idles at
  72 °C and 31 W; 40 s after a 60 s full-chip load it still idles at 81 °C and 36.5 W. Take baselines at the same temperature,
  interleave runs, or fit a temperature term.
- **Power depends on the data:** fp32 TensorFMA at the same 546 cycles per op draws 38.3 W with zero operands, 46.7 W with ones
  (π the same), 61.3 W with random uniform and 63.4 W with random normal values, every run launched as the die cools through
  81→80 °C (`tools/ettelem/run_horace_strict.sh`; run-to-run spread under 0.1 W). Heating follows power over idle (36.3 W there):
  1, 27 and 76 m°C per 10¹² FLOPs for zeros, ones and random normal. The cause is in the RTL (`rtl-sim/fma_toggle`): a lane whose
  A or B operand word is zero gets no valid, so its pipeline registers are not clocked; a constant clocks 2.47 M register bits per
  op and toggles nothing (3 fJ per clocked bit); random data also flips 87 M counted nets per op, 85% of them in the multiplier
  tree, but the energy is mostly in the rest of the unit (0.8 fJ per toggle against 0.03 fJ in the tree). That model predicts the
  board power of 14 patterns to 0.5 W out of sample. Thermal step response of the sensor to board power: 0.06 °C/W after 1 s,
  0.12 after 3 s, 0.16 after 7 s (stages of 1.5 s and 10 s), more beyond a minute.
- **Leakage dominates an idle card:** idle board power is 12.6 W + 23.3 W x exp((T - 80)/36) from 64 to 88 °C (26.7 W at 62 °C,
  36.3 W at 80 °C). The thermal network from board power to the sensor has stages at 1.5 s (0.11 °C/W), 4 s (0.05), 60 s (0.23),
  150 s (0.14), 400 s (0.86) and 2,500 s (0.08): 1.47 °C/W in all on this card in its desktop chassis, so the leakage loop gain
  is 0.95 at 80 °C and passes one at 82 °C. From an 80 °C start random fp32 data reaches 90 °C in 19 to 26 s, ones in 107 to 167 s,
  random data on 256 of 1,024 cores in about 5 minutes; zeros cool. `tools/ettelem/flip_thermal_model.py` fits all of this and
  `tools/ettelem/predict_heat.py` applies it to custom operand tiles (time to 90 °C within 12% in the median).
- **Zero gating looks at the bit pattern:** -0.0 is not gated (46.7 W, like ones, against 38.2 W for +0.0). Mask with a select,
  not by multiplying by zero. Dense structured matrices (DCT, kaleidoscope products, circulant, rank 1) cost what random data
  costs; sparse structure (butterfly factors, bands, blocks) costs by its surviving products; a Hadamard matrix costs 50 W.
- **Per work unit, over idle, at 0.52 V and 600 MHz:** 8 pJ per integer instruction, 0.32 pJ per int8 multiply-add, 2.7 pJ per
  fp16, 6.0 pJ per fp32 (random data), 0.3 pJ per bit streamed from L2 SRAM, 18 pJ per bit from LPDDR4x. Power is linear in
  active minions (26 mW each on random fp32). The 0.62 V / 800 MHz operating point switches 2.0x the power (V²f says 1.9x).
- **The temperature sensor reads whole degrees.** Use step times, not levels: fit the heating power that reproduces a run's
  readings through the thermal network (`analyze_horace_strict.py`). It agrees with the electrical power to about 1 W.
- **Rail figures are ~2 s moving averages;** board power is near-instantaneous. Skip 2-3 s after a step before averaging.
- **Board minus the three rails** (DDR, PCIe, Maxions, IO, regulator loss; no sensors) is 15 W idle, ~21 W under matmul or DRAM load.
- `tools/ettelem` reads the per-rail snapshot the stock CLI refuses (`DM_CMD_GET_SP_STATS`), samples the full telemetry set 45
  times a second, and reads the per-shire on-die voltage map (`loglevel debug` + `sptrace`; restore with `loglevel info`).
- **The clock governor is thermal first.** Above its 65 °C software threshold the service processor holds the lowest
  operating point (600 MHz, 0.52 V), whatever the power: that is why every hot run sat at 600 MHz even at 70 W. Below 65 °C
  a busy card is stepped up to 800 MHz at 0.62 V (700 MHz at 0.57 V in between) while the board's average power is under the
  65 W TDP level, and stepped back down as the die passes 65 °C. From a 63 °C start, zeros hold 800 MHz for a whole 7 s run
  (11.6 TFLOPS), random data is back at 600 MHz within a second (9.3 TFLOPS). For like-for-like power numbers start runs
  well above 65 °C (`tools/ettelem/run_horace_strict.sh`) and check `mhz` in the telemetry.

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
- **Measured on aifoundry2's card, 2026-09-18** (`kernels/mmbench`, 1024 minions at 600 MHz, exact results):

  | Type | Cycles per 16×16×K op | Throughput per minion | Share of peak | Chip total |
  |---|---|---|---|---|
  | fp32 (K = 16) | 529 (512 ideal) | 15.5 flop/cycle | 97% | 9.5 TFLOP/s |
  | fp16→fp32 (K = 32) | 529 (512 ideal) | 31 flop/cycle | 97% | 19.0 TFLOP/s |
  | int8→int32 (K = 64) | 280 (256 ideal) | 117 op/cycle | 91% | 71.8 TOP/s |

  So int8 runs at 8× fp32's rate, not 4×: 4× the K per op, and each op takes half the cycles. Board power was 57–62 W
  under load and 31 W at idle.
- Encodings, as decoded by sw-sysemu's `insns/tensors.cpp`, which is the most precise spec available:
  - The `tensor_fma` type field is bits 3:1: 0 = fp32, 1 = fp16→fp32, 3 = int8→int32.
  - For all three, the A-columns field counts 32-bit words, so 15 means K = 16 / 32 / 64.
  - B lines hold 16 columns × E consecutive k-values per 32-bit word: E = 1 for fp32, 2 for fp16, 4 for int8.
  - fp16 accumulates in fp32 with round-toward-zero.
  - int8 accumulates in TenC. Set bit 23 on the last op to copy it into f0..f31.
  - Row i of C lives in `f[2i]`, `f[2i+1]`.
  - Before reading those registers with ordinary vector instructions, insert `fmv.x.w x0, f0` (errata 1.29 type F).
- The inner loop that reaches these numbers is the one gp-sdk's autogenerated matmul uses:
  1. Issue the A `tensor_load` into L1Scp lines 0-15 or 16-31, alternating between ops (`dst_start` bit 57).
  2. Issue the B `tensor_load` with TenB (id 1).
  3. `tensor_wait` on id 0.
  4. `tensor_fma`, with `scp_loc_a` switching between the same two buffers.

  The next op's loads overlap the running FMA. No FMA wait is needed inside the loop.

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
