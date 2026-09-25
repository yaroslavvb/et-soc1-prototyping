<!-- Research notes behind the GPU comparison in docs/reports/2026-09-18-et-soc1-on-chip-communication.html.
     Compiled 2026-09-18 from the cited sources; ET-SoC-1 numbers in the report are our own measurements. -->

# GPU on-chip communication: sourced numbers for the ET-SoC-1 comparison

Compiled 2026-09-18. Every number carries a type label and a source key; the keys are listed in the References section at the end.

**Type labels**
- **measured**: a benchmark on real hardware.
- **vendor spec**: a statement or specification from NVIDIA or Esperanto.
- **estimate**: an author's rule of thumb, a projection, or a value read off a plot.
- **derived**: my own arithmetic on cited values.

**Clock conversions**
- A100 cycles are converted at 1410 MHz (0.709 ns/cycle). That is the A100 boost clock ([W] Table 4), the maximum clock of the A100 PCIe in [L25] Table 2, and the clock Chips and Cheese observed under load.
- H800 PCIe cycles are converted at 1755 MHz (0.570 ns/cycle), from [L25] Table 2.
- H100 SXM5 values from [CF25], [CR26] and [DGNA] are left in cycles because those papers do not state the clock.

**Verification.** Numbers were checked against the primary text, table or chart image, or, for [BB24], the released raw logs. Where only part of a source was checked, the entry says so. Sources are paraphrased rather than quoted; each entry gives a table, figure or section locator instead.

---

## Key numbers at a glance

| Item | Quantity | Value | GPU (clock) | Type | Source |
|---|---|---|---|---|---|
| 1a | L2 hit, near partition | 208.0 cyc = 147.5 ns | A100 PCIe 40GB (1410 MHz) | measured | [L25] Table 4 |
| 1a | L2 hit, far partition | 356.6 cyc = 252.9 ns | same | measured | [L25] Table 4 |
| 1a | L2 near / far plateaus | ≈145–157 ns / ≈304–313 ns | A100 SXM4 40GB | measured | [CCd] |
| 1b, 1c | Cross-SM handoff through an L2 atomic: two threads ping-pong a counter with CAS; time per one-way handoff | 165.55 ns (≈233 cyc, derived) | A100 | measured | [CC23] |
| 1c | Same idea, full round trip (ping + pong), flag in HBM | 315.5 ns (≈158 ns one-way, derived) | GH200 (Hopper) | measured | [F24] Fig. 13 |
| 1c | `__threadfence()` between two global read-modify-writes, per fence | ≈764 cyc = 542 ns | A100 PCIe 40GB (1.41 GHz) | measured | [BB24] raw logs |
| 2 | `grid.sync()` | 1.122 µs; 1.2 µs | A100 (PCIe) | measured | [Z23] Fig. 3; [EB23] §5 |
| 2 | `grid.sync()` range | 1.43 µs (1 block/SM × 32 threads) to 24.5 µs (32 blocks/SM) | V100 (1312 MHz) | measured | [Z20] Fig. 5 |
| 2 | Kernel boundary used as a barrier | launch overhead 1.503 µs; API call → kernel start 2.26 µs | A100; A100-SXM4-80GB | measured | [Z23] Fig. 3; [V25] Table V |
| 2 | CUDA Graphs | A100 grid-to-grid latency 2.0–4.0× lower than streams (vendor); H100 launch about 1.3 µs with graphs vs 2.1 µs without (measured) | A100; H100 | vendor spec; measured | [W] Fig. 30; [HR25] |
| 3 | `__syncthreads()` | 23 cyc (1 warp) to 85 cyc (32 warps) | A100 PCIe (1.41 GHz) | measured | [BB24] |
| 3 | `__shfl_sync`, dependent chain | 25 cyc (17.7 ns) | A100 PCIe | measured | [BB24] |
| 3 | Shared-memory load | 23 cyc (16.3 ns); 29 cyc in pointer-chase tests | A100 | measured | [A] Table IV, [Sun23] Table 10; [L25] Table 3 |
| 4 | DSMEM remote access (SM to SM) | 181 cyc = 103 ns at cluster size 2; 184–213 cyc for cluster sizes 2–16 | H800 PCIe (1755 MHz) | measured | [L25] §7.1 |
| 4 | DSMEM remote access | ≈190–203 cyc across cluster sizes 2–16; 191 cyc | H100 SXM5 | measured | [CF25] Fig. 5; [CR26] Table II |
| 4 | SM to SM through global memory | 1110 cyc = 632 ns (paper v1: 956 cyc); over 470 cyc | H800 PCIe; H100 SXM5 | measured | [L25] §7.1; [CF25] §2.3 |
| 4 | DSMEM aggregate bandwidth (ring copy) | 3.28 TB/s at cluster 2, 2.78 TB/s at cluster 4 | H800 PCIe | measured | [L25] §7.2 |
| 4 | `cluster.sync()`, 2 CTAs on different SMs | 851 cyc | H100 SXM | measured | [CR26] Table II |
| 4 | DSMEM vs global-memory data exchange | about 7× faster | H100 | vendor spec | [WH] p.30 |
| 5 | Small-vector device-wide reduction | **No A100 measurement found.** CUB DeviceReduce on 10⁶ floats: 9.4 µs (A40). Cluster-level reduce of 32–256 KB: 6.8–9.2 µs (H100) | A40; H100 | measured | [P26] Table III; [CF25] Table 1 |
| 6a | L2 data-movement energy | 4.71 pJ/bit (37.7 pJ/B, derived) | A100 SXM4 40GB | measured (system level) | [S25] Table 3 |
| 6b | On-chip wire energy | ≈100 fJ/bit/mm (14 nm and recent talks); 20–40 fJ/bit-mm (16 nm era) | — | estimate | [DTH20]; [D23]; [D18] |
| 6c | On-chip transport energy, MCM-GPU parameter table | ≈80 fJ/bit (no distance stated) | — | estimate | [MCM17] Table 2 |
| 6d | Die and SMs | 826 mm², 54.2 B transistors, TSMC N7, 108 of 128 SMs | A100 | vendor spec | [W] p.14, Table 4 |
| 7 | ET-SoC-1 die | 570 mm², TSMC 7 nm, over 24 B transistors | ET-SoC-1 | vendor spec | [MICRO22] pp.31, 37 |

---

## 1. A100 inter-SM communication (no direct SM-to-SM path; goes through L2 and global memory)

**Architecture (vendor spec)**
- A100's L2 is split into two partitions. Each partition caches data for the SMs in the GPCs wired directly to it, and hardware coherence spans the whole GPU ([W] p.35).
- Each partition has 40 slices of 512 KB. L2 read bandwidth is 5120 B/clk ([W] p.35).
- NVIDIA describes the L2 as a split L2 with a hierarchical crossbar, giving 2.3× V100's bandwidth and lower latency ([HC20] slide 19; [W] p.16).
- Global-memory atomics are executed near memory, in the L2 ([HC20] slide 20).

### 1a. L2 hit latency, near and far partitions

| Near | Far | GPU, clock | Method | Type | Source |
|---|---|---|---|---|---|
| 208.0 cyc (147.5 ns) | 356.6 cyc (252.9 ns) | A100 PCIe 40GB, 1410 MHz max | Fine-grained pointer chase, 32 B stride. Per-access latencies grouped by K-means into near hit, far hit, near miss (474.9 cyc) and far miss (622.7 cyc) | measured | [L25] Table 4 |
| 202.8 cyc (143.8 ns) | 408 cyc (289.4 ns), upper plateau | same | Random-stride pointer chase, averaged; latency steps up at half and at full L2 capacity | measured | [L25] Table 3, §4.1 |
| 218 cyc (≈155 ns, derived) | 379 cyc (≈269 ns, derived) | A100 40GB, variant and clock not stated | One SM warms a line, another SM times a plain `ld.global` with `clock()`. Values are the centres of a two-component Gaussian mixture | measured | [DGNA] §5.2, Fig. 5a |
| 200 cyc, one value | — | A100, variant and clock not stated | Pointer chase | measured | [A] Table IV |
| 261.5 cyc, one value | — | A100 PCIe | Pointer chase with `.cg` loads | measured | [L24] Table IV |
| ≈145–157 ns (0.5–16 MB footprint) | ≈304–313 ns (28–38 MB footprint) | A100 SXM4 40GB (Lambda Cloud) | CUDA pointer chase, "Prefer L1" configuration. DRAM plateau ≈408–411 ns | measured | [CCd] |

**Hopper, for context**
- H800 PCIe: near hit 258.0 cyc (147.0 ns), far hit 414.1 cyc (236.0 ns); [L25] Table 4.
- H100 SXM5: local 295 cyc, remote 470 cyc ([DGNA] §5.2). Within the local partition there are two sub-levels, 280 vs 312 cyc ([DGNA] §5.2).
- H100 (Lambda Cloud; the Chips and Cheese article [CC23] identifies it as the PCIe card): ≈139–160 ns near, ≈289–298 ns far ([CCd]).

**Disagreement.** The far-partition figure varies with method:
- 356.6 cyc, from clustering individual accesses ([L25]).
- 379 cyc ([DGNA]).
- About 430–441 cyc, derived from the Chips and Cheese nanosecond plateaus.

The near-partition figure agrees across sources at about 200–220 cycles, or about 145–157 ns.

### 1b. Latency of global-memory atomics

**Not found:** a single-thread, uncontended round-trip latency for `atomicAdd`, `atomicExch` or `atomicCAS` on A100, in any source I could open. The closest measurements are below.

- **A100: 165.55 ns. H100 PCIe: 161.14 ns** [measured]. Source: [CC23], chart *Global Atomic Latency*.
  - Method, checked in the benchmark source: OpenCL, two work-groups of one thread each. The threads bounce a 32-bit counter with `atomic_cmpxchg`, each incrementing it only after the other has.
  - The host divides elapsed time by 2 × iterations, so the value is the time per successful CAS, i.e. one **one-way handoff** through L2. It is contended by design.
  - SM placement is not controlled, and only one pair was measured.
  - Derived: ≈233 cycles at 1410 MHz.
- **Same test inside one SM** (shared/local-memory atomics, both threads in one work-group): **A100 43.97 ns, H100 36.47 ns** [measured]. Source: [CC23], chart *Local Atomic Latency*.
- **V100, older context** [measured]. Source: [J19] §4.2, Table 4.2.
  - Global-memory atomics: 36 cycles uncontended, rising to 76 cycles with 32 threads contending. T4: 76 cycles; P100: 26 cycles.
  - Shared-memory atomics: V100 6 cycles; T4 8 cycles.
  - Method: the atomic is followed by a dependent load of known latency, and the atomic's share of the pair's latency is deduced.
  - Caveat, my interpretation: 36 cycles is far below V100's L2 hit latency (≈193 cycles in Jia et al.'s Volta report). So this is not a full SM→L2→SM round trip; read it as the atomic's pipeline cost.
- **Vendor statements about A100 atomics:**
  - Throughput of global-memory atomics is up 11× for FP16 and 2.7× for FP32 compared with V100 ([W] p.56).
  - Atomics are performed near memory ([HC20] slide 20).
  - Neither source gives a latency.

### 1c. Producer–consumer flag handoff between SMs through global memory

| Value | GPU | What was measured | Type | Source |
|---|---|---|---|---|
| **165.55 ns one-way** (≈233 cyc) | A100 | CAS ping-pong between two work-groups (entry 1b above) | measured | [CC23] |
| **161.14 ns one-way** | H100 PCIe | same | measured | [CC23] |
| **315.5 ns full round trip** (≈158 ns one-way, derived) | GH200 Hopper, two threads on different SMs | 1-byte flag padded to two cache lines, flag in HBM; ping sets PING if the flag holds PONG, pong does the reverse, using `cuda::std::atomic` CAS. With the flag in Grace LPDDR: 810.2 ns | measured | [F24] §III-E2, Fig. 13 (H0–H0 cell) |
| **1110 cyc = 632 ns** | H800 PCIe, 1755 MHz | SM-to-SM transfer through global memory, described as one store plus one load. Method details not given. Paper v1 (Jan 2025) reported 956 cyc (545 ns); v2 (Sep 2025) reports 1110 | measured | [L25] §7.1 |
| over 470 cyc | H100 SXM5 | Global-memory reference line in the SM-to-SM latency plot | measured | [CF25] §2.3, Fig. 5 |
| **≈764 cyc = 542 ns per fence** | A100-PCIE-40GB, 1.41 GHz | Loop body is: global RMW, `__threadfence()`, global RMW; minus a baseline without the fence. 1 block, 1–8 threads. Rises to ≈791 cyc at 128–256 threads and falls to 599 cyc at 1024 | measured | [BB24] raw logs (`cuda_threadfence_array`, step 1) |

**Derived estimate for one message on A100.** A message is a data store, a `__threadfence()`, a flag store and the consumer's poll. That costs about 542 ns for the fence plus about 166 ns for the flag handoff, so roughly **0.7 µs** end to end. These two parts were never measured together.

**Disagreement.** On Hopper, both [CC23] and [F24] put the one-way handoff at about 160 ns. [L25]'s store-plus-load figure is 3.5–4× larger (545–632 ns), and [CF25] reports over 470 cycles. The methods differ, and [L25] and [CF25] do not describe theirs in detail.

---

## 2. Grid-wide synchronization and kernel launch

### `grid.sync()` (cooperative groups)
- **A100: 1,122 ns** [measured]. Source: [Z23], SC23 Doctoral Showcase poster, Fig. 3 (bar labels).
  - Configuration: occupancy 12.5%.
  - Method: follows [Z20]. The poster labels the GPU A100-PCIE elsewhere.
  - Other GPUs on the same figure: V100 1,330 ns, P100 1,627 ns, RTX 3090 643 ns.
- **A100-PCIe: 1.2 µs** [measured]. Source: [EB23] (EBISU, ICS '23), in the section that quantifies device-tiling overhead; methodology follows [Z20]. Setup: NVCC 11.5, Xeon E5-2650 host.
- **V100** (DGX-1, default clock 1312 MHz) [measured]. Source: [Z20] Fig. 5.
  - Method: two kernels with different repeat counts, timed with a host clock; latency = difference in time ÷ difference in repeat count. This gives the average cost of back-to-back barriers.

  | Blocks per SM | Latency | Threads per block |
  |---|---|---|
  | 1 | 1.43 µs | 32 |
  | 1 | 2.21 µs | 1024 |
  | 2 | 1.81–3.49 µs | 32–1024 |
  | 4 | 2.85–4.52 µs | 32–512 |
  | 8 | 5.07–6.71 µs | 32–256 |
  | 32 | 19.29–24.51 µs | 32–64 |

  - Latency grows mainly with blocks per SM, not threads per block (§V-C).
  - P100 minimum: 1.77 µs.
  - The authors say grid sync is always slower than the kernel-launch overhead, but by a negligible margin: at most 2.5 µs at 2 blocks per SM (§V-C).
- **Vendor:** NVIDIA says cooperative-launch grid synchronization overhead was reduced by up to 30% for A100/CUDA 11 ([W] p.67). No absolute value is given.
- **H100 `grid.sync()`:** not found.

### Kernel launch as the implicit global barrier
- **A100: 1,503 ns launch overhead** [measured]. Source: [Z23] Fig. 3. V100: 1,161 ns; RTX 3090: 1,025 ns. This is the extra cost of one more kernel in a stream, measured with the kernel-fusion method of [Z20] §IX-B.
- **A100-SXM4-80GB: 2,260.5 ns from the start of `cudaLaunchKernel` to kernel start** [measured]. Source: [V25] Table V, Eq. (1).
  - Null-kernel duration: 1,440.0 ns.
  - H100 PCIe: 2,374.6 ns launch, 1,235.2 ns duration. GH200: 2,771.6 ns, 1,171.2 ns.
  - Method: CUPTI timestamps via the PyTorch profiler. Setup: CUDA 12.6.
- **V100** [measured]. Source: [Z20] Table I.
  - Launch overhead: 1,081 ns (traditional), 1,063 ns (cooperative), 1,258 ns (cooperative multi-device).
  - The same table lists "null kernel total latency" of 8,888, 10,248 and 10,874 ns.
- **V100, per-kernel wall time for 2.9 µs kernels** [measured]. Source: [Gr19]. Setup: CUDA 10.1.
  - 9.6 µs when synchronizing after every kernel.
  - 3.8 µs with launches overlapped in a stream.
  - 3.4 µs with a CUDA Graph.
  - Derived: about 0.9 µs overhead per kernel with streams and 0.5 µs with graphs.

### CUDA Graphs
- **A100 vs V100, graph vs stream speedup** [vendor spec]. Setup: 32-node graphs of empty kernels, on DGX-1V and DGX-A100 ([G20] slide 28).

  | Metric | Graph shape | V100 | A100 |
  |---|---|---|---|
  | CPU launch speedup | straight line | 6.6× | 7.2× |
  | CPU launch speedup | single fork-join | 16.2× | 18.2× |
  | CPU launch speedup | repeated fork-join | 6.0× | 26.6× |
  | Grid-to-grid latency speedup | straight line | 1.5× | 2.0× |
  | Grid-to-grid latency speedup | single fork-join | 2.2× | 3.7× |
  | Grid-to-grid latency speedup | repeated fork-join | 1.5× | 4.0× |

  Sources: CPU launch from [W] Fig. 29 (p.60); grid-to-grid from [W] Fig. 30 (p.61). No absolute times are given.
- **CUDA 12.6 repeat-launch CPU cost** for straight-line graphs of 10 or more nodes: about 2.5 µs + ~1 ns per node, down from 2 µs + 200 ns per node in CUDA 11.8 [measured by vendor]. Setup: RTX 3060 (Ampere) with a Xeon Silver 4208 ([HO24]).
- **H100: about 2.1 µs per launch on a stream vs about 1.3 µs with CUDA graphs** [measured]. Source: [HR25]. Method: a dummy kernel that records a start time, sleeps and records an end time. The H100 variant is not stated.

---

## 3. Intra-SM communication on A100 (context)

**Source for the A100 barrier, shuffle and `__syncwarp` numbers:** [BB24] (IISWC 2024).
- The paper's figures show an RTX 4090. The A100 data comes from the authors' released raw logs for A100-PCIE-40GB, which record a clock rate of 1.41 GHz.
- Method: `clock64()` time of an unrolled loop (1000 iterations × 100 unroll) with two operations per step, minus a baseline with one. Medians of 7 runs.
- For back-to-back barriers and dependent shuffles, the time per operation equals the latency.

**`__syncthreads()` (BAR.SYNC), one block** [measured]

| Threads per block | Warps | Cycles per barrier | Time |
|---|---|---|---|
| 1–32 | 1 | 23 | 16.3 ns |
| 64 | 2 | 25 | |
| 128 | 4 | 29 | |
| 256 | 8 | 37 | |
| 512 | 16 | 53 | |
| 1024 | 32 | 85 | 60.3 ns |

- With 2 blocks per SM (216 blocks): 64 cycles at 512 threads; median 122.7 cycles at 1024 threads.
- Derived: the single-block values fit ≈21 + 2 × (warps per block).
- **V100:** 22 cycles as seen from one warp; P100: 218 cycles ([Z20] Table II) [measured].

**Warp shuffle, `__shfl_sync`** [measured]
- A100: 25 cycles (17.7 ns) for 32-bit data at 1–512 threads per block; 31 cycles at 1024 threads ([BB24]). The benchmark is a dependent chain, `x = __shfl_sync(…, x, …)`.
- V100: 22 cycles (tile group); P100: 31 cycles ([Z20] Table II).

**`__syncwarp()`** [measured]
- A100: 5 cycles at 1–256 threads, 6 at 512, 7 at 1024 ([BB24]).
- V100: tile-group sync 14 cycles ([Z20] Table II).

**Shared-memory load latency** [measured]
- **23 cycles** (16.3 ns). Sources:
  - [A] Table IV: `ld.shared` 23 cycles, `st.shared` 19.
  - [Sun23] Table 10: `ld.shared.u32` 23.0 cycles with no bank conflict; 25.0 / 29.0 / 37.0 cycles for 2-, 4- and 8-way conflicts.
  - [Sun23] Table 9: `ldmatrix.x1/.x2/.x4` 23.1 / 25.1 / 29.3 cycles.
- **29 cycles** (20.6 ns) by pointer chase ([L24] Table IV; [L25] Table 3).
- L1 hit: 33 cycles ([A] Table IV; [L25] Table 3).
- H800 shared memory: 29 cycles ([L25] Table 3). H100 SXM: 30 cycles ([CR26] Table II).

**Warp reduction (vendor).** A100 added a hardware warp-wide reduce instruction (used by the Cooperative Groups `reduce` API). It gives the result in one step, where earlier GPUs needed 5 SHFL steps ([W] p.67, Fig. 35). No latency for `redux.sync` was found.

**Cross-SM vs intra-SM (derived).** Using A100 numbers:
- An L2 hit (≈148–253 ns) is 9–15× a shared-memory load (16 ns).
- A one-way flag handoff through L2 (≈166 ns) is ≈10× a `__syncthreads()` of one warp and ≈3× one of 32 warps.
- A `grid.sync()` (≈1.1–1.2 µs) is ≈70× a 1-warp barrier.

---

## 4. H100/H800 distributed shared memory (thread block clusters)

**Vendor spec**
- H100 has a dedicated SM-to-SM network that links the SMs within a GPC, and clusters get hardware-accelerated barriers ([WH] p.29).
- Threads can load, store and perform atomics on other SMs' shared memory (DSMEM). NVIDIA says DSMEM makes data exchange between thread blocks about 7× faster than going through global memory ([WH] p.30; also [HB]).
- The portable maximum cluster size is 8; H100 allows 16 as a non-portable option ([HTG] §1.4.1.3).
- DSMEM can be used at the same time as L2, so their bandwidths add ([HTG] §1.4.1.3).
- **No bandwidth spec for the SM-to-SM network was found.**

### Latency

| Value | GPU, clock | Setup | Type | Source |
|---|---|---|---|---|
| **181 cyc = 103 ns** at cluster size 2, about 30% below the L2 near hit (258 cyc) | H800 PCIe, 1755 MHz | Blocks of one thread pinned to different SMs (checked with `%smid`), pointer chase | measured | [L25] §7.1 |
| **184–213 cyc (105–121 ns)** across cluster sizes 2–16 | same | same | measured | [L25] §7.1 |
| 29 cyc local shared memory; 33 cyc when a block reads its own shared memory through the DSM interface | same | same | measured | [L25] §7.1 |
| 180 cyc, about 32% below L2 | H800 PCIe | Two blocks of one thread each, `clock()` | measured | [L24] §IV-E |
| **≈190 cyc at cluster size 2**, vs over 470 cyc through global memory | H100 SXM5 80GB, clock not stated | DSMEM latency microbenchmark | measured | [CF25] §2.3 |
| Cluster sizes 2 / 4 / 8 / 16: ≈190 / 203 / 202 / 195 cyc | same | Read off the Fig. 5 bar chart (only the 190 value is in the text) | estimate | [CF25] Fig. 5 |
| **191 cyc remote vs 30 cyc local** | H100 SXM, CUDA 13.0, clock not stated | Dependent-load chain, 2 CTAs forced onto different SMs, median of 15 runs | measured | [CR26] Table II |

**How latency varies with cluster size.** It is essentially flat: about 180–213 cycles from cluster size 2 to 16 in two independent studies. Remote DSMEM costs about 6× a local shared-memory load and about 0.7× an L2 near hit.

### Bandwidth
- **H800 PCIe, ring copy** [measured]:
  - Aggregate 3.27 TB/s at cluster size 2 and 2.65 TB/s at cluster size 4 ([L24] Fig. 8).
  - 3.28 TB/s and 2.78 TB/s in [L25] §7.2, Fig. 10.
  - Derived, assuming all 114 SMs take part: ≈28.8 GB/s ≈ 16.4 B/clk per SM at cluster size 2.
  - A broadcast pattern loses throughput as clusters grow ([L25] Fig. 9).
  - A block reading its own shared memory through the DSM interface gets 205 GB/s, against 225 GB/s theoretical per SM. The paper calls this 80%; the arithmetic gives 91%.
- **H100 SXM5** [measured]. Source: [CF25] §2.3, Fig. 5.
  - About 3.35 TB/s at cluster size 2 (plot reading), falling to **2.90 TB/s at cluster size 16**, just below global memory's 2.96 TB/s.
  - Active SMs fall from 132 to about 112 as clusters grow (plot reading).
- **H100 SXM, one CTA pair** [measured]. Source: [CR26] Table II.

  | | Local | Remote (DSMEM) |
  |---|---|---|
  | Read | 20.89 B/cycle | 4.77 B/cycle |
  | Store | 27.67 B/cycle | 21.37 B/cycle |

### `cluster.sync()`
- **851 cycles** for a cluster of 2 CTAs on different SMs, H100 SXM [measured] ([CR26] Table II). RTX 5090: 404 cycles.
- **How it scales with cluster size: not found.** Lühnen et al., HPEC 2024 (below) probably covers it, but I could not access that paper.

### TMA
- A TMA load takes about 170 cycles longer than a regular load at the same footprint, on H800 [measured] ([L25] §5.1).
- **Multicast: no peer-reviewed or vendor numbers found.** One informal forum report (NVIDIA Developer Forums thread 355253, Jan 2026) on H100 80GB (132 SMs):
  - Without multicast: about 38 B/clk per SM from L2, just under 5,120 B/clk GPU-wide.
  - With 4-way cluster multicast: about 70 B/clk per SM, with no further gain at 8-way.
  - The poster notes that multicast raises average latency.
  - Treat this as informal ([NVF26]).

---

## 5. Reductions on one GPU

- **A100, small vector (KB to about 1 MB): no published measured latency found** for CUB DeviceReduce, `thrust::reduce`, a single-pass atomics reduction or a cooperative-groups reduction.
- **Ampere (A40, not A100)** [measured]. Source: [P26] Table III.
  - CUB DeviceReduce on float32: **9.4 ± 0.4 µs for 10⁶ elements (4 MB)** and 75.6 ± 0.3 µs for 10⁷.
  - Timed with CUDA events around the kernels; excludes host launch overhead.
- **V100** [estimate, plot reading]. Source: [Z20] Fig. 15.
  - At the smallest size plotted (about 0.4 MB), one reduction takes roughly 25 µs with CUB, about 30 µs with an implicit (kernel-boundary) barrier, and about 45 µs with `grid.sync`.
  - At large sizes all methods run at 849–865 GB/s ([Z20] Table VI, measured).
- **H100 cluster-level reduce over DSMEM** [measured]. Source: [CF25] Table 1.

  | Data size | ClusterReduce, on-chip (DSMEM) | ClusterReduce, off-chip (global memory) | ClusterGather, on-chip | ClusterGather, off-chip |
  |---|---|---|---|---|
  | 32 KB | 6.77 µs | 8.03 µs | 3.90 µs | 6.26 µs |
  | 256 KB | 9.17 µs | 22.44 µs | 4.15 µs | 6.61 µs |

  - ClusterGather ranges over 3.90–4.39 µs on-chip and 6.26–6.61 µs off-chip across the sizes tested.
  - The setup is not described, so these numbers probably include launch cost.
- **Published "latency floor" for an all-reduce among SMs: not found.**
- **Derived floor for A100.** A device-wide reduce-then-broadcast needs at least one grid-wide barrier (≈1.1–1.2 µs) or one kernel boundary (≈1.5–2.3 µs). A tree through L2 adds at least two L2 round trips (≈0.3–0.5 µs) plus a fence (≈0.54 µs). So the floor is about **1–2 µs** per all-reduce.

---

## 6. Energy of on-chip data movement

### 6a. Measured cache-level energy
Source: [S25] Table 3 (SC'25) [measured]. These are whole-GPU dynamic energies from microbenchmarks, split into control and datapath components, so they include instruction and address overhead.
- The L2 figure also includes the SM↔L2 crossbar; the paper does not separate the two.
- Hardware per the SC'25 text: A100 SXM4 40GB; the "GH200" row is its Hopper GPU (132 SMs, 50 MB L2).

| GPU | L2 (control + datapath) | L1 | HBM |
|---|---|---|---|
| A100 | **3.11 + 1.60 = 4.71 pJ/bit** (37.7 pJ/B, derived) | 1.59 pJ/bit | 13.11 pJ/bit |
| GH200 | **4.87 pJ/bit** | 1.45 pJ/bit | 11.68 pJ/bit |

### 6b. On-chip wire energy per bit per mm (Dally, Keckler, NVIDIA Research)

| Value | Node | What it is | Type | Source |
|---|---|---|---|---|
| 240 fJ/bit/mm per transition | 40 nm | Wire energy. Projected 150 fJ/bit/mm (10 nm, high frequency) and 115 fJ/bit/mm (10 nm, low voltage). Moving 256 bits 10 mm costs 310 pJ at 40 nm | projection | [K11] Table 1 |
| 20–40 fJ/bit-mm | Chips of the day; the paper's examples are 16 nm | CMOS-driven wire, ~CV² with C ≈ 200 fF/mm, which the authors say does not scale. They expect no improvement because supply voltage scales slowly | estimate | [D18] "On-chip communication" section |
| ≈100 fJ/bit-mm | 14 nm | Cost of moving data to and from 8 KB SRAM subarrays. Same sidebar: 8 KB local memory 50 fJ/bit; a 100 MB memory about 0.7 pJ/bit | estimate | [DTH20] sidebar |
| ≈100 fJ/b-mm | Not stated (2023 talk) | Communication rule of thumb | estimate | [D23] slides 8, 45 |

**Worked examples in these sources**
- A 48 mm round trip across a 28 mm GPU die costs 4.8 pJ/b ([D23] slide 31).
- An 80-SM GPU moving 4 TB/s over a 20 mm average distance needs 26 W at 40 fJ/bit-mm ([D18]).

**Measured NVIDIA on-chip links (link energy, including transceivers)**
- Ground-referenced signaling link: **170 fJ/b/mm** at 16 Gb/s, 28 nm, built as a test site inside a 600 mm² production GPU ([T18] abstract, §VIII).
- Charge-recycling bus: 6.5–23.3 fJ/b/mm, 16 nm FinFET. This figure is from the paper's title only; I did not open the full text ([W16]).

**Not found:** an NVIDIA wire-energy figure labelled 7 nm or 5 nm.

**Derived, for A100** (826 mm², about 28.7 mm on a side if square), at 100 fJ/bit-mm:
- Crossing half the die (≈14 mm) costs ≈1.4 pJ/bit.
- A corner-to-corner Manhattan trip (≈57 mm) costs ≈5.7 pJ/bit.
- For comparison, [S25]'s measured system-level L2 energy is 4.71 pJ/bit.

### 6c. NoC and crossbar energy per bit in GPUs
- **MCM-GPU parameter table** [estimate] ([MCM17] Table 2):

  | Domain | Energy |
  |---|---|
  | On-chip | ≈80 fJ/bit (no distance stated) |
  | On-package | 0.5 pJ/bit |
  | On-board | 10 pJ/bit |
  | System | 250 pJ/bit |

- **NVIDIA vendor documents** give no per-hop or per-bit energy for the A100 L2 crossbar or the H100 SM-to-SM network ([W]; [WH]; [HB]).
- **H100 DSMEM energy per access: not published** in anything I found.
- **Non-GPU reference for a mesh NoC:** FlooNoC reports 0.15 pJ/B/hop at 0.8 V in 12 nm FinFET, a post-layout figure for an open-source mesh NoC ([FN25]).

### 6d. Die size and SM count [vendor spec]
- **A100 (GA100):**
  - TSMC 7 nm N7, 54.2 B transistors, 826 mm² ([W] p.14; Table 4, pp.36–37).
  - The full GA100 has 128 SMs; A100 has 108 ([W] pp.19–20).
  - 40 MB L2; 1410 MHz boost.
- **H100 (GH100):**
  - TSMC 4N, 80 B transistors, 814 mm² ([WH] p.17).
  - The full GH100 has 144 SMs; SXM5 has 132 and PCIe has 114 ([WH] p.18; Table 3, pp.39–40).
  - 50 MB L2.

---

## 7. ET-SoC-1 facts (published sources, plus two local design documents)

**Chip [vendor spec]**
- TSMC 7 nm, over 24 B transistors, **570 mm²** die, 89 mask layers ([MICRO22] pp.31, 37; [HC33] slide 20).
- 1,088 ET-Minions and 4 ET-Maxions ([HC33] slide 2).
- The datasheet counts 1,093 RISC-V cores, which includes 1 service processor ([DS] §1).
- 34 Minion shires of 32 minions plus 4 MB SRAM each ([DS] §2.1; [MICRO22] p.35).
- Typically 32 shires compute and 1 manages ([DS] §2.1).
- Typical power under 20 W, adjustable from 10 to 60+ W ([HC33] slide 20; [MICRO22]).

**Mesh NoC [vendor spec]**
- The datasheet describes an 8 × 6 grid containing 34 Minion shires, 8 memory shires, 1 PCIe shire and 1 I/O shire. The corners are empty, leaving 44 mesh stops ([DS] §4).
- The mesh runs on its own low-voltage domain ([MICRO22] p.35).
- Inside a shire, the four 1 MB SRAM banks connect to the neighborhoods through a 512-bit crossbar ([MICRO22] p.35).

**NoC width and bandwidth**
- Each shire's L2 enters the NoC through 512-bit To_L3 and To_Sys ports ([SCS] §1).
- The NoC delivers up to 32 GB/s into each memory shire over a 512-bit AXI path ([DS] §7.1.1).
- Derived: 64 B × 500 MHz = 32 GB/s, consistent with the clock below.
- **No per-link or bisection bandwidth figure is published.**

**NoC clock**
- The design document lists `clk__noc` at 500 MHz for the Main and Debug NoC ([SHD] clock table).
- Firmware sets a 400 MHz NoC PLL by default and allows 300–500 MHz in its voltage table ([FW]).
- Caveat: the core-et documents come from the repository's erbium branch. They are design documents and may differ from shipped silicon.

**Messaging and synchronization**
- **Hot Chips 33 announcements** [vendor spec] ([HC33] slides 8–10):
  - Instructions for fast local synchronization within a group.
  - Send-to-neighbor and receive-from-neighbor instructions.
  - Per-shire fast local atomics, barriers and credit counters, plus IPI support.
- **Neighborhood Fast Local Messaging Network** [design document] ([NMAS] §4.7):
  - Wired for tensor-reduction patterns: a fixed binary-tree pairing of the 8 minions.
  - Messages up to 256 bits.
  - Latency of 1 cycle.
  - At most one message every other cycle per sender.
- **Published performance figures for TensorReduce, fast local barriers or credit counters: none found.**

**Third-party measurements** (Martin Chang, [MC26], Apr 2026) [measured]
- **Bandwidth:**
  - Shire-pair TensorLoadL2SCP of 960 B chunks: **5.92 GB/s per direction**, the same when both directions run at once.
  - 16 disjoint neighbour flows: 166–167 GB/s aggregate.
  - No link congestion was observed; the only contention found was at the source shire's read bandwidth.
  - The observed topology is a mesh with some links missing.
- **Latency:** atomics show a baseline of about **120 cycles plus about 6 cycles per mesh hop**, i.e. about 3 cycles per direction.
- **Clock caveat:** Chang's companion tool etTopoScan converts cycles to time assuming a 600 MHz minion clock ([TOPO] `topo_scan.cpp` line 286). Any GB/s figure computed that way scales with the real clock.
- **What it does not report:** no systolic-matmul or FlashAttention result. The post names FlashAttention and matrix multiplication on llama.cpp as the author's goal and measures only bandwidth and latency (re-read on 2026-09-24 at https://clehaxze.tw/gemlog/2026/04-27-tnvestigating-the-et-soc-1-noc.gmi).
- **Differs from docs/et-soc1-notes.md:** it gives 20 ns (12 minion cycles at 600 MHz) per mesh hop for a round trip, a different operation.

**Sources disagree**
- On-die SRAM: over 160 MB ([HC33]; [MICRO22]) vs 140 MB ([DS] §1).
- Minion clock: 300 MHz–2 GHz operating range, 500 MHz–1.5 GHz typical ([HC33], 2021) vs 300–800 MHz (AI Foundry, 2025).
- Power: under 20 W ([HC33]; [MICRO22]) vs 40 W (AI Foundry, 2025).

---

## Disagreements and caveats (summary)
1. **A100 far-L2 latency:** 356.6 cyc [L25], 379 cyc [DGNA], 408 cyc upper plateau [L25] Table 3, and about 430–441 cyc derived from the [CCd] nanosecond values.
2. **Hopper SM-to-SM through global memory:**
   - About 160 ns one-way handoff ([CC23]; [F24]).
   - 956 cyc in paper v1 vs 1110 cyc in v2 of the same paper ([L25]).
   - Over 470 cyc ([CF25]).
3. **A100 shared-memory latency:** 23 cyc from dependent `ld.shared` timing ([A]; [Sun23]) vs 29 cyc by pointer chase ([L24]; [L25]).
4. **A100 launch overhead:** 1.5 µs ([Z23]) vs 2.26 µs ([V25]). The first is the extra cost of one more kernel in a stream; the second runs from the start of the API call to kernel start.
5. **[L25] internal inconsistencies:**
   - DSM own-shared-memory efficiency is stated as 80%, but 205/225 = 91%.
   - The global-memory handoff changed between v1 and v2, from 956 to 1110 cycles.
6. **Cycle counts from `clock()`** are converted at maximum clocks. Real clocks may have been lower under load; [S25] §5.3 observed an A100 drop from 1410 to 1350 MHz at TDP.

## Not found, or found but not accessible (unverified)
**Not found**
- Single-thread, uncontended A100 round-trip latency for `atomicAdd`, `atomicExch` or `atomicCAS`.
- H100 `grid.sync()` latency.
- How `cluster.sync()` scales with cluster size.
- A100 small-vector CUB reduce latency.
- H100 DSMEM energy.
- GPU NoC energy per hop.
- NVIDIA 7 nm or 5 nm wire energy.
- A vendor bandwidth figure for the SM-to-SM network.
- Measured benefit of TMA multicast in a paper.

**Not accessible; worth fetching by hand**
- **Jin, Rocca, Kim, Kasan, Rhu, Bakhoda, Aamodt, Kim, "Uncovering Real GPU NoC Characteristics: Implications on Interconnect Architecture", MICRO 2024.** It measures SM-to-L2 latency and bandwidth by SM location on V100, A100 and H100, which is directly relevant here. The PDF was too large for the fetch tool, and the per-GPU numbers seen only in search snippets are unverified.
- **Lühnen, Marschner, Lal, "Benchmarking Thread Block Cluster", HPEC 2024.** Likely has `cluster.sync()` against cluster size; the server refused connections.
- **Jia and Van Sandt, "Dissecting the Ampere GPU Architecture through Microbenchmarking", GTC 2021 S33322.** It may include A100 atomic latency; the session page did not render.
- **Dally, Keckler, Kirk, "Evolution of the Graphics Processing Unit (GPU)", IEEE Micro 2021.** Paywalled.
- **WikiChip ET-SoC-1 page.** Connection refused; its reported 1,024-bit mesh link width is unverified.

---

## References
- **[W]** NVIDIA, *NVIDIA A100 Tensor Core GPU Architecture* whitepaper V1.0 (2020). https://images.nvidia.com/aem-dam/en-zz/Solutions/data-center/nvidia-ampere-architecture-whitepaper.pdf
- **[WH]** NVIDIA, *NVIDIA H100 Tensor Core GPU Architecture* whitepaper V1.01 (2022). https://resources.nvidia.com/en-us-tensor-core/gtc22-whitepaper-hopper (mirror: https://www.advancedclustering.com/wp-content/uploads/2022/03/gtc22-whitepaper-hopper.pdf)
- **[HB]** Andersch et al., "NVIDIA Hopper Architecture In-Depth", NVIDIA Technical Blog, 22 Mar 2022. https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/
- **[HTG]** NVIDIA, *Hopper Tuning Guide*, §1.4.1.3. https://docs.nvidia.com/cuda/hopper-tuning-guide/index.html
- **[HC20]** J. Choquette, W. Gandhi, "NVIDIA A100 GPU: Performance & Innovation for GPU Computing", Hot Chips 32 (2020). https://hc32.hotchips.org/assets/program/conference/day1/HotChips2020_GPU_NVIDIA_Choquette_v01.pdf
- **[G20]** R. Krashinsky, O. Giroux, "Inside the NVIDIA Ampere Architecture", GTC 2020 S21730. https://developer.download.nvidia.com/video/gputechconf/gtc/2020/presentations/s21730-inside-the-nvidia-ampere-architecture.pdf
- **[A]** H. Abdelkhalik, Y. Arafa, N. Santhi, A. Badawy, "Demystifying the Nvidia Ampere Architecture through Microbenchmarking and Instruction-level Analysis", IEEE HPEC 2022. https://arxiv.org/abs/2208.11174
- **[L24]** W. Luo et al., "Benchmarking and Dissecting the Nvidia Hopper GPU Architecture", arXiv 2402.13499 (2024). https://arxiv.org/abs/2402.13499
- **[L25]** W. Luo et al., "Dissecting the NVIDIA Hopper Architecture through Microbenchmarking and Multiple Level Analysis", arXiv 2501.12084: v1 Jan 2025, v2 Sep 2025. https://arxiv.org/abs/2501.12084
- **[DGNA]** C. Liu, Y. Chen, T. E. Carlson, "DGNA: Dissecting GPU NUMA Architecture through Microbenchmarking and Data Analysis", arXiv 2607.19922 (Jul 2026). https://arxiv.org/abs/2607.19922
- **[CCd]** Chips and Cheese, "Latency Data Graphing and Reference", raw data for the entries "NVIDIA A100 SXM4 (Prefer L1)" and "NVIDIA H100 (Prefer L1)" (Lambda Cloud). https://jsmemtest.chipsandcheese.com/latencydata
- **[CC23]** C. Lam, "Nvidia's H100: Funny L2, and Tons of Bandwidth", Chips and Cheese, Jul 2023, charts *Global Atomic Latency* and *Local Atomic Latency*. https://chipsandcheese.com/p/nvidias-h100-funny-l2-and-tons-of-bandwidth. Benchmark code: https://github.com/clamchowder/Microbenchmarks (`GpuMemLatency/atomic_test.c`, `kernel.cl`)
- **[F24]** L. Fusco, M. Khalilov, M. Chrapek, G. Chukkapalli, T. Schulthess, T. Hoefler, "Understanding Data Movement in Tightly Coupled Heterogeneous Systems: A Case Study with the Grace Hopper Superchip", arXiv 2408.11556 v2 (2024), §III-E2, Fig. 13. https://arxiv.org/abs/2408.11556
- **[J19]** Z. Jia, M. Maggioni, J. Smith, D. P. Scarpazza, "Dissecting the NVidia Turing T4 GPU via Microbenchmarking", Citadel technical report, arXiv 1903.07486 (2019), §4.2, Table 4.2. https://arxiv.org/abs/1903.07486
- **[BB24]** B. A. Burtchell, M. Burtscher, "Characterizing CUDA and OpenMP Synchronization Primitives", IEEE IISWC 2024. https://userweb.cs.txstate.edu/~burtscher/papers/iiswc24b.pdf. A100 raw data (logs `cuda_syncthreads`, `cuda_shfl_sync`, `cuda_syncwarp`, `cuda_threadfence_array`): https://github.com/burtscher/SyncPerformance/tree/main/results/system2/NVIDIA_A100-PCIE-40GB
- **[Z20]** L. Zhang, M. Wahib, H. Zhang, S. Matsuoka, "A Study of Single and Multi-device Synchronization Methods in Nvidia GPUs", IEEE IPDPS 2020 (Tables I, II, VI; Figs. 5, 15). https://arxiv.org/abs/2004.05371
- **[Z23]** L. Zhang, M. Wahib, T. Endo, S. Matsuoka, "Overcoming the Gap Between Compute and Memory Bandwidth in Modern GPUs", SC23 Doctoral Showcase poster, Fig. 3. https://github.com/neozhang307/doctoral_showcase_materials/blob/main/SC23_Poster_DoctorShowCase.pdf
- **[EB23]** L. Zhang et al., "Revisiting Temporal Blocking Stencil Optimizations" (EBISU), ACM ICS 2023. https://arxiv.org/abs/2305.07390
- **[V25]** P. Vellaisamy et al., "Characterizing and Optimizing LLM Inference Workloads on CPU-GPU Coupled Architectures", IEEE ISPASS 2025, Table V. https://arxiv.org/abs/2504.11750
- **[Gr19]** A. Gray, "Getting Started with CUDA Graphs", NVIDIA Technical Blog, Sep 2019. https://developer.nvidia.com/blog/cuda-graphs/
- **[HO24]** Hoffman, Oh, "Constant Time Launch for Straight-Line CUDA Graphs and Other Performance Enhancements", NVIDIA Technical Blog, Sep 2024. https://developer.nvidia.com/blog/constant-time-launch-for-straight-line-cuda-graphs-and-other-performance-enhancements
- **[HR25]** B. Spector, J. Juravsky et al., "Look Ma, No Bubbles!", Hazy Research blog, 27 May 2025. https://hazyresearch.stanford.edu/blog/2025-05-27-no-bubbles
- **[Sun23]** W. Sun, A. Li, T. Geng, S. Stuijk, H. Corporaal, "Dissecting Tensor Cores via Microbenchmarks: Latency, Throughput and Numeric Behaviors", IEEE TPDS 2023, Tables 9–10. https://arxiv.org/abs/2206.02874
- **[CF25]** X. Luo et al., "ClusterFusion: Expanding Operator Fusion Scope for LLM Inference via Cluster-Level Collective Primitive", arXiv 2508.18850 (2025), §2.3, Fig. 5, Table 1. https://arxiv.org/abs/2508.18850
- **[CR26]** Z. Li, T.-W. Huang, U. Ogras, "CREDIT: Cost-guided Reduction-reuse with Efficient DSMEM Inter-CTA Tiling", accepted to HPEC 2026, arXiv 2609.01864, Table II. https://arxiv.org/abs/2609.01864
- **[NVF26]** NVIDIA Developer Forums, thread 355253 on TMA multicast (post of 5 Jan 2026), informal. https://forums.developer.nvidia.com/t/355253
- **[P26]** E. Pilliat, "High-Performance Portable GPU Primitives for Arbitrary Types and Operators in Julia", arXiv 2603.18695 (2026), Table III. https://arxiv.org/abs/2603.18695
- **[S25]** O. Antepara, Z. Zhao, B. Austin, N. Ding, L. Oliker, N. J. Wright, S. Williams, "Benchmark-driven Models for Energy Analysis and Attribution of GPU-Accelerated Supercomputing", SC'25, Table 3. https://escholarship.org/uc/item/6189368s
- **[K11]** S. W. Keckler, W. J. Dally, B. Khailany, M. Garland, D. Glasco, "GPUs and the Future of Parallel Computing", IEEE Micro 31(5), 2011, Table 1. https://www.cs.toronto.edu/~pekhimenko/courses/csc2224-f19/docs/GPU.pdf
- **[DTH20]** W. J. Dally, Y. Turakhia, S. Han, "Domain-Specific Hardware Accelerators", CACM 63(7), 2020, cost-model sidebar. https://doi.org/10.1145/3361682
- **[D18]** W. J. Dally, C. T. Gray, J. Poulton, B. Khailany, J. Wilson, L. Dennison, "Hardware-Enabled Artificial Intelligence", Symposium on VLSI Circuits 2018. https://research.nvidia.com/sites/default/files/pubs/2018-06_Hardware-Enabled-Artificial-Intelligence/VLSI2018_HardwareAI.pdf.PDF
- **[D23]** W. J. Dally, "Energy Efficiency and AI Hardware", Stanford AHA Retreat keynote, 31 Aug 2023, slides 8, 31, 45. https://aha.stanford.edu/sites/g/files/sbiybj20066/files/media/file/aha-retreat-2023_dally_keynote_en_eff_ai_hw_0.pdf
- **[T18]** W. J. Turner, J. W. Poulton, J. M. Wilson et al., "Ground-Referenced Signaling for Intra-Chip and Short-Reach Chip-to-Chip Interconnects", IEEE CICC 2018. https://research.nvidia.com/sites/default/files/pubs/2018-04_Ground-Referenced-Signaling-for/CICC2018_GRS_18-5.pdf
- **[W16]** J. Wilson et al., "A 6.5-to-23.3fJ/b/mm Balanced Charge-Recycling Bus in 16nm FinFET CMOS at 1.7-to-2.6Gb/s/wire …", ISSCC 2016. https://research.nvidia.com/publication/2016-02_65-233fjbmm-balanced-charge-recycling-bus-16nm-finfet-cmos-17-26gbswire-clock
- **[MCM17]** A. Arunkumar et al., "MCM-GPU: Multi-Chip-Module GPUs for Continued Performance Scalability", ISCA 2017, Table 2. https://research.nvidia.com/sites/default/files/publications/ISCA_2017_MCMGPU.pdf
- **[FN25]** T. Fischer, M. Rogenmoser, T. Benz, F. K. Gürkaynak, L. Benini, "FlooNoC: A 645 Gbps/link 0.15 pJ/B/hop Open-Source NoC …", IEEE TVLSI 33(4), 2025. https://arxiv.org/abs/2409.17606
- **[MICRO22]** D. R. Ditzel and the Esperanto team, "Accelerating ML Recommendation With Over 1,000 RISC-V/Tensor Processors on Esperanto's ET-SoC-1 Chip", IEEE Micro 42(3):31–38, 2022. Open copy: https://www.esperanto.ai/wp-content/uploads/2022/05/Dave-IEEE-Micro.pdf
- **[HC33]** D. Ditzel et al., "Accelerating ML Recommendation with over a Thousand RISC-V/Tensor Processors on Esperanto's ET-SoC-1 Chip", Hot Chips 33 (2021). https://hc33.hotchips.org/assets/program/conference/day2/HC2021.Esperanto.Dave_Ditzel.presentation.v1submitted.pdf
- **[DS]** Esperanto, *ET-SoC-1 Preliminary Datasheet* Rev 1.0, §§1, 2.1, 4, 7.1.1. https://github.com/aifoundry-org/et-man (local copy: `external/et-man/`)
- **[SCS]** *CORE-ET Shire Cache Specification*, §1. **[SHD]** *CORE-ET Minion Shire Description*, clock table. **[NMAS]** *CORE-ET Neighborhood MAS*, §4.7. All from the core-et repository, erbium branch, `docs/` (local copy: `external/core-et/docs/`).
- **[FW]** et-platform firmware:
  - `device-bootloaders/src/ServiceProcessorBL2/common/main.c`: NoC PLL mode comment, 400 MHz.
  - `device-bootloaders/src/ServiceProcessorBL2/services/thermal_pwr_mgmt.c`: NoC range 300–500 MHz.
  - Repository: https://github.com/aifoundry-org/et-platform (local copy: `external/et-platform/`, commit 836a4ab).
- **[MC26]** M. Chang, "Investigating the ET-SoC-1 NoC", AI Foundry blog, 30 Apr 2026. https://blog.aifoundry.org/p/investigating-the-et-soc-1-noc (originally on clehaxze.tw, 27 Apr 2026)
- **[TOPO]** M. Chang, etTopoScan, `host/topo_scan.cpp` line 286. https://github.com/marty1885/etTopoScan (local copy: `external/etTopoScan/`)
