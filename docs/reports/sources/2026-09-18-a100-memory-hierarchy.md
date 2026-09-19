<!-- Research notes behind the A100 column of docs/reports/2026-09-18-et-soc1-memory-hierarchy.html.
     Compiled 2026-09-18 from the cited sources; ET-SoC-1 numbers in the report are our own measurements. -->

# A100 memory hierarchy: a model built from published sources

Cycles are converted to ns at 1410 MHz boost (1 cycle = 0.709 ns). Chips and Cheese saw A100 clocks go "to 1410 MHz under load and stays there" [CC]. At TDP, the clock can drop to 1350 MHz [S] §5.3. "Derived" means my arithmetic on cited values. Source keys are listed at the end.

## 1. Capacity

| Level | Per SM | Chip | Source |
|---|---|---|---|
| Registers | 64K × 32-bit = 256 KB | 27,648 KB | [W] Table 4; [T] "Occupancy" |
| L1 + shared | 192 KB unified. Shared = 0/8/16/32/64/100/132/164 KB, L1 gets the rest. Max 163 KB per block | 20.25 MB (derived) | [W] p.33; [T] "Unified Shared Memory/L1" |
| L2 | — | 40 MB = 2 partitions × 40 slices × 512 KB. Each partition serves the GPCs attached to it | [W] p.35 |
| L2 seen from one SM | — | About 20 MB at near latency. Past about 20 MB, data "cannot be replicated in both L2 cache sections" | [E]; [CCd] |
| HBM | — | 40 GB HBM2 (5 stacks, 10 × 512-bit MCs) or 80 GB HBM2e | [W] pp.19, 35; [D] |

## 2. Load-to-use latency (pointer chase)

[L24] and [L25] measured an A100 PCIe 40GB. [CCd] measured an SXM4 40GB; its PCIe-40GB curves agree within about 2%. [A] does not state the variant or clock. No 80GB latency data was found.

| Level | Cycles | ns | Source |
|---|---|---|---|
| Register (dependent FP32 `mad`) | 4 | 2.8 | [A] Table II |
| Shared load | 23; 29.0 | 16.3; 20.6 | [A] Table IV; [L24] Table IV, [L25] Table 3 |
| L1 hit | 33; 37.9; 33.0; about 39 (derived) | 23.4; 26.9; 23.4; **27.6** | [A] Table IV; [L24] Table IV; [L25] Table 3; [CCd] "A100 SXM4 (Prefer L1)", ≤128 KB |
| L2 near | 200; 202.8; 208.0 "near hit"; about 205–221 (derived). [L24] reports a single L2 value of 261.5 | 142; 144; 148; **145–157** at 0.5–16 MB | [A] Table IV; [L25] Tables 3–4; [CCd] |
| L2 far | 356.6 "far hit"; 408 upper plateau; about 420–441 (derived) | 253; 289; **298–313** at 28–38 MB | [L25] Tables 4, 3; [CCd]. [E] notes a far-section "intermediate plateau" |
| HBM | 566; near/far miss 474.9/622.7; about 573–579 (derived) | 401; 337/442; **406–411** at 64 MB–1 GB | [L25] Tables 3–4; [CCd] |
| HBM, low outliers | 466.3; 290 | 331; 206 | [L24] Table IV; [A] Table IV. The [A] value uses `ld.cv` and is probably not a real DRAM access (my inference) |
| TLB | On SXM4-80GB, random-line throughput "drops off precipitously" past a 64 GB window; the author infers "each SM group has its own 64GB TLB". The NVLink Link TLB has "a reach of 64 GB" | — | [Wk] §1.3, §3; [T] §1.4.3. **Page-walk latency: not found** |

## 3. Bandwidth

| Level | Peak | Measured | Source |
|---|---|---|---|
| Registers | Not published | — | **Not verified** |
| Shared / L1 | 32 banks × 32 bit/clk = **128 B/clk/SM**, giving 19.5 TB/s over 108 SMs (derived) | Shared: 128.0 B/clk/SM. L1: 99.5–120 B/clk/SM (PCIe). L1: "close to 128B/cycle/SM". L1: **14.8 TB/s** on SXM4 40GB | [BP]; [L24] Table V, [L25] Table 5; [E] gpu-cache; [S] Table 1 |
| L2 | **5,120 B/clk** read = 80 slices × 64 B/clk, about 7.2 TB/s (derived); "2.3x" V100 | **4.5 TB/s** over the full L2 (variant unstated). **4.3 TB/s** on SXM4 40GB. About 2.8 TB/s on PCIe (2,007.9 B/clk) | [W] p.35; [G] slide 24; [CC]; [S] Table 1; [L25] Table 5 |
| HBM | **1,555 GB/s** for 40GB (HBM2, 5120-bit, 1215 MHz DDR). 1,935 GB/s for 80GB PCIe. **2,039 GB/s** for 80GB SXM | 40GB: **1,407 GB/s** (PCIe); 1.4 TB/s (SXM4). 80GB SXM4: BabelStream Triad **1,774 GB/s** (87%). Random 128-B lines: 1.4–1.6 TB/s | [W] Table 4; [D]; [L25] Table 5; [S] Table 1; [B]; [Wk] §2.1 |

## 4. Energy

| Item | Value | Node and assumptions | Source |
|---|---|---|---|
| HBM2 device | **3.97 pJ/bit** (§1). Also 3.92 = 1.21 activation + 2.24 on-die movement + 0.30 I/O, incl. ECC (§2). 909 pJ per 1 KB row activation | Model with 28 nm DRAM parameters scaled from 55 nm, 2 Gb/s/pin. A100 runs 2.43 Gb/s/pin | [O] §1–2, §4.2, Fig. 1, Table 3 |
| HBM2, "circa 7 nm" | 250–450 pJ per 64-bit access = 3.9–7.0 pJ/bit | Footnote says this is "only the I/O energy" | [J] Table 2 |
| HBM2e device | "about **4.3 pJ/bit**" | SK hynix vendor statement; conditions not stated | [H] §III |
| A100 "HBM" level, measured | **13.11 pJ/bit** (8.47 control + 4.64 datapath) | Incremental over L1+L2, so it includes the memory controllers and L2-to-MC transport. N7, SXM4 40GB | [S] Table 3 |
| A100 L2, measured | **4.71 pJ/bit** (3.11 + 1.60) | Whole-GPU dynamic energy, including instruction and address overhead | [S] Table 3 |
| A100 L1, measured | **1.59 pJ/bit** (1.26 + 0.33); shared memory not separated | Same | [S] Table 3 |
| 7 nm SRAM (generic) | 8 KB: 7.5; 32 KB: 8.5; 1 MB: 14 pJ per 64-bit access (0.12–0.22 pJ/bit) | Update of Horowitz's 45 nm table | [J] Table 2 |
| SRAM, 2011 projection | 64-bit read from 8 KB: 14 pJ (40 nm), 2.4/1.8 pJ (10 nm) | Projection | [K] Table 1 |
| Wire | 240 fJ/bit/mm per transition (40 nm), 150/115 (10 nm); about 0.06–0.08 pJ/bit/mm at 50% toggle (derived) | Projection; no measured 7 nm GPU value found | [K] Table 1 |

Dally's recent keynotes quote **45 nm** Horowitz values (32b 8 KB SRAM read 5 pJ; DRAM 640 pJ) [DH]. These are not 7 nm numbers. The AccelWattch and GPUWattch papers tabulate no per-access pJ values.

## 5. Board context

TDP is 400 W for SXM4 (40GB and 80GB), 250 W for PCIe 40GB and 300 W for PCIe 80GB [D]. Constant power is **54 W** on SXM4 40GB ([S] Table 2). The authors attribute much of it to HBM refresh, which they put at about 40 W for 40 GB ([S] §4). An anecdotal nvidia-smi reading on an SXM4-80GB shows 78 W at 0% utilization in P0 [F].

## 6. Recommended single values (1410 MHz)

| Cell | Value | Confidence | Why |
|---|---|---|---|
| Capacities | 256 KB RF, 192 KB L1+smem per SM; 40 MB L2 (2×20); 40/80 GB | High | NVIDIA documentation |
| Shared latency | 29 cyc / 21 ns | Med-high | Two Luo papers agree; [A] reports 23 |
| L1 latency | 33 cyc / 23 ns | High | [A] and [L25] agree |
| L2 near | 208 cyc / 148 ns | High | Three sources within about 6% |
| L2 far | 357 cyc / 253 ns (C&C up to 313 ns) | Medium | Only [L25] isolates it |
| HBM latency | 570 cyc / 405 ns | High | [L25] and C&C agree within 3% |
| Shared/L1 BW | 19.5 TB/s peak; 14.8 sustained | High / med | Documented bank width plus measurements |
| L2 BW | 7.2 peak; **4.4 TB/s** sustained | High / med | Two SXM4 measurements (4.3, 4.5); PCIe gives 2.8 |
| HBM BW | 1.40 TB/s (40GB), 1.77 (80GB) sustained | High / med | 80GB rests on one run |
| HBM energy | 4.0 (HBM2) / 4.3 (HBM2e) pJ/bit device; 13 system | Medium / med-low | A model and a vendor statement, plus one A100 study |
| L2 energy | 4.7 pJ/bit system (array about 0.2) | Med-low / low | [S] only; array figure is generic 7 nm |
| L1 energy | 1.6 pJ/bit system (array about 0.13) | Med-low / low | Same |
| RF energy | about 0.12 pJ/bit (8 KB SRAM proxy) | Low | No A100 data |
| Wire | about 0.07 pJ/bit/mm | Low | A 2011 projection |
| Idle | 54 W | Medium | One peer-reviewed measurement |

If your ET numbers come from board power, compare against the "system" values from [S]. Use the device or array values against circuit-level estimates.

## 7. Not verified

- Delestrac et al., ASAP 2024: an A100 per-level energy study that includes shared memory. Paywalled, and HAL blocks automated access.
- Dally, Keckler, Kirk, IEEE Micro 2021: no full text available.
- GTC'21 S33322, Ampere dissection by Jia and Van Sandt: not accessible. The Jia et al. arXiv papers cover only Volta and Turing.
- TunneLs, CCS'23 (A100 TLB): not accessible.
- Page-walk latency, register-file bandwidth and energy, and all 80GB latencies.

## Sources

- [W] "NVIDIA A100 Tensor Core GPU Architecture" whitepaper: https://images.nvidia.com/aem-dam/en-zz/Solutions/data-center/nvidia-ampere-architecture-whitepaper.pdf
- [D] "NVIDIA A100 Tensor Core GPU Data Sheet" (Jun 2021): https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/a100/pdf/nvidia-a100-datasheet-us-nvidia-1758950-r4-web.pdf
- [T] "NVIDIA Ampere GPU Architecture Tuning Guide": https://docs.nvidia.com/cuda/ampere-tuning-guide/index.html
- [BP] "CUDA C++ Best Practices Guide", Shared Memory section: https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html
- [G] GTC 2020 S21730, "Inside the NVIDIA Ampere Architecture": https://developer.download.nvidia.com/video/gputechconf/gtc/2020/presentations/s21730-inside-the-nvidia-ampere-architecture.pdf
- [A] Abdelkhalik et al., "Demystifying the Nvidia Ampere Architecture through Microbenchmarking and Instruction-level Analysis" (2022): https://arxiv.org/abs/2208.11174
- [L24] Luo et al., "Benchmarking and Dissecting the Nvidia Hopper GPU Architecture" (2024): https://arxiv.org/abs/2402.13499
- [L25] Luo et al., "Dissecting the NVIDIA Hopper Architecture through Microbenchmarking and Multiple Level Analysis" (2025): https://arxiv.org/abs/2501.12084
- [CC] Lam, "Nvidia's H100: Funny L2, and Tons of Bandwidth", Chips and Cheese (2023): https://chipsandcheese.com/p/nvidias-h100-funny-l2-and-tons-of-bandwidth
- [CCd] Chips and Cheese, "Latency Data Graphing and Reference" (raw data; entries "NVIDIA A100 SXM4/PCIE", Lambda Cloud): https://jsmemtest.chipsandcheese.com/latencydata
- [E] Ernst, gpu-benches README: https://github.com/te42kyfo/gpu-benches
- [S] Antepara et al., "Benchmark-driven Models for Energy Analysis and Attribution of GPU-Accelerated Supercomputing", SC'25: https://escholarship.org/uc/item/6189368s
- [B] BabelStream issue #137, A100-SXM4-80GB output (Hammond, 2022): https://github.com/UoB-HPC/BabelStream/issues/137
- [Wk] Walker, "Enabling full-speed random access to the entire memory on the A100 GPU" (2024): https://arxiv.org/abs/2405.11425
- [O] O'Connor et al., "Fine-Grained DRAM: Energy-Efficient DRAM for Extreme Bandwidth Systems", MICRO 2017: https://www.cs.utexas.edu/~skeckler/pubs/MICRO_2017_Fine_Grained_DRAM.pdf
- [H] Moon et al. (SK hynix), "Advanced Packaging Technologies in Memory Applications for Future Generative AI Era", IEDM 2023: https://iedm23.mapyourshow.com/mys_shared/iedm23/handouts/15-6_Tue_14482.pdf
- [J] Jouppi et al., "Ten Lessons From Three Generations Shaped Google's TPUv4i", ISCA 2021: https://gwern.net/doc/ai/scaling/hardware/2021-jouppi.pdf
- [K] Keckler et al., "GPUs and the Future of Parallel Computing", IEEE Micro 2011: https://www.cs.toronto.edu/~pekhimenko/courses/csc2224-f19/docs/GPU.pdf
- [DH] Dally, "Hardware for Deep Learning", Hot Chips 2023: https://hc2023.hotchips.org/assets/program/conference/day2/Keynote%202/Keynote-NVIDIA_Hardware-for-Deep-Learning.pdf
- [F] NVIDIA forum, "A100-SXM-80GB Enforced Power Limit different from server to server": https://forums.developer.nvidia.com/t/a100-sxm-80gb-a100-enforced-power-limit-different-from-server-to-server/184219
