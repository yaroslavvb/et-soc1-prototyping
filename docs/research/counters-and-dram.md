# ET-SoC-1 performance counters, cache controls and DRAM configuration

This page lists the knobs available for splitting a memory access on the lab cards into its parts: L1, L2, read buffer, NoC, L3, memshire, and DRAM row/column. For each knob it says what a **U-mode kernel launched through the runtime can do on firmware `353f20e`** and what would need M-mode or a firmware change.

**Status:** research only, as of 2026-09-19. Nothing here has been checked on silicon yet; the "verify" items are the first experiments to run.

**Citations:**
- `PRM:<n>` is a line in `external/et-man/txt/ET Programmer's Reference Manual.txt`. The section number is given too.
- `Errata <x.y>` uses the table-of-contents numbering of `ET-SoC Errata`. In the text body the headings are shifted by one: §1 items appear as "2.x" and §3 items as "4.x".
- `DS:<n>` is the Preliminary Datasheet text.
- `fw:<path>:<n>` is `external/et-platform` at commit `353f20e`. Every firmware file cited here is unchanged at HEAD `836a4ab`.
- `CET:` is `external/core-et` (erbium branch).
- `SCspec` is `core-et/docs/CORE-ET-Shire-Cache-Specification.pdf`.

---

## 0. Answers for the evict-then-time-one-load experiment

### (a) What `dst` means in EvictVA (CSR 0x89F)

**The level semantics.** EvictVA "writes-back (if needed) the line … from all cache levels between <L1> and <DestLevel-1> to level <DestLevel>. The line … is invalidated in all levels from <L1> through <DestLevel-1>" (PRM:6161-6190, §8.4).

| `dst` | Effect |
|---|---|
| 0 = L1 | NOP (PRM:6193) |
| 1 = L2 | Line leaves L1. It stays, or is written back, in the shire's L2. |
| 2 = L3 | Line leaves L1 and L2. It stays, or is written back, in its home L3 slice. |
| 3 = MEM | Line leaves L1, L2 and the L3 slice. The next load goes to DRAM. |

**Restrictions:**
- `dst` = L3 or MEM on an L2-scratchpad address raises a bus-error interrupt (PRM:6190).
- The operation is a NOP on a hard-locked line.

**Things to know before relying on it:**
- **Erbium clamps Evict/Flush destinations.** The Erbium RTL forces destinations L3/Mem down to L2 (`CET:rtl/.../intpipe_csr_file.v:2056`, `legalize_cacheop_dest`); only Prefetch may target L3/Mem there. The ET-SoC-1 PRM allows L3/Mem, and the shire-cache spec has explicit L3 Evict/EvictWData opcodes (SCspec §4.9). So on ET-SoC-1 it should work, but **verify** it: time a load after `dst=3` against one after `dst=2`. The expected numbers are ~440 ns and ~280 ns (the memhier results).
- **The firmware only cleans L1 and L2 between kernels.** After each kernel it evicts L1 to L2 and the whole local L2 (fw:MachineMinion/src/syscall.c:313-333). It does **not** touch L3 unless the kernel was launched with the `flushL3` option (see §6).
- **Nothing blocks U-mode cacheops.** `minion_feature.trap_on_u_cacheops` (CET csr.csv:58-62) can make U-mode cacheops trap, but no firmware code writes `minion_feature`.

### (b) Is the cacheop asynchronous, and how do you wait for it?

Yes, it is asynchronous. The PRM protocol is:
1. `fence` **before** the cacheop, so earlier memory operations are done (PRM:5919-5923, §8.1.3).
2. `csrwi tensor_wait, 6` **after** it, before any load or store to the affected line. Event 6 means "all previous cacheops are complete" (PRM:8685-8700, 8740).

In code, this is `WAIT_CACHEOPS` in fw:et-common-libs/include/etsoc/isa/utils.h:96-99. The firmware itself does `evict…; WAIT_CACHEOPS; FENCE` (fw:MachineMinion/src/syscall.c:348-420).

**The `id` in `x31[0]` does not wait for an evict.** It only matters for PrefetchVA (TensorWait 4/5) (PRM:6420-6440; fw:et-common-libs/include/etsoc/isa/cacheops-umode.h:178-189).

**Other rules:**
- Wait for an L1 prefetch with TensorWait 6 followed by `fence` (PRM:8702).
- Cacheop throughput is limited by `ucache_control.CacheOp_Max`, which the firmware sets to 8 per minion (fw:MachineMinion/src/syscall.c:420).
- Do not set `CacheOp_Max` to 0 (Errata 1.4).

### (c) Line size and prefetchers

- **Lines are 64 B everywhere:** L1, L2, L3 and scratchpad (DS:340-344; SCspec §1).
- **There is no hardware prefetcher** in the L1, L2, L3 or memshire. The only prefetch is the software PrefetchVA / REQ_Prefetch (core-et agent survey of SCspec §3.12 and `dcache_defines.vh`).
- **The L2 read buffer is not a prefetcher.** It is an 8-entry fully-associative buffer of recently read clean L2/SCP lines, per bank. It explains the measured 36-cycle "RBUF" step against a 47-cycle L2 hit.
- **Memshire:** the umctl2 has no prefetch.

### (d) Address mapping and page policy

**Full chain (§3.4):**

```
PA[5:0]   byte in 64 B line
PA[7:6]   L2 bank (local shire)             PA[9:8] L2 sub-bank
PA[10:6]  L3 home shire (default swizzle)   PA[12:11] L3 bank, PA[14:13] L3 sub-bank
PA[8:6]   memshire (0-3 west, 4-7 east)     PA[9]   controller (channel) within memshire
PA[12:10] DRAM bank (8 banks)               PA[5:1],PA[17:13] column (10 bits, 2 KB page/channel)
PA[34:18] DRAM row (17 bits)
```

**Page policy is open-page:**
- `SCHED.pageclose=0` and `SCHED1.pageclose_timer=0` (fw:etsoc-hal/src/memshire_ddr_init_functions.c SCHED=0x00a01f01).
- `ddrc_main_ctl` auto-precharge is left at 0 (fw:device-bootloaders/.../mem_controller.c:245).
- A row therefore stays open until a conflict or a refresh closes it.

**Two parts of the map are inferred (details in §3.4):**
- The memshire/channel bits come from a tool comment and NoC mask values, not from a programmed register.
- The bank/row/column bits are decoded from ADDRMAP values.

**What the map implies for experiments:**
- **Row hit:** two lines 1 KB apart (PA differs only in bit 10+) land on the same channel. With a PA[12:10] difference they land in different banks.
- **Row conflict:** a PA difference of 256 KB (bit 18) keeps the same channel, bank and column group but changes the row.
- **Same row, different line:** vary PA[17:13].

---

## 1. Minion hart performance counters (neighbourhood PMU)

### 1.1 Hardware

**Architecture (PRM:264-278, §1.3):**
- The standard RISC-V counters are moved into one PMU per neighbourhood of 8 minions.
- `mcycle`, `minstret`, `cycle` and `instret` read 0.
- `mhpmcounter9-31` and `mhpmevent9-31` are tied to 0.

**Counters (PRM:373-492, §1.3.2; CET/rtl/shire/neigh/neigh_pmu.v:56-245):**
- **Minion counters.** `mhpmcounter3-6` exist twice per neighbourhood: one copy shared by all even harts (thread 0 of each minion), one by all odd harts. Each copy counts the **union/sum** of the events that each of those 8 harts selected in its own `mhpmevent`, up to +8 per cycle.
- **Neighbourhood counters.** `mhpmcounter7-8` exist twice (thread 0 / thread 1 copies). They count at most +1 per cycle. When harts disagree, the lowest `mhartid`'s selection wins.
- **Width.** Counters are 64 bits: a 7-bit pre-counter plus a 57-bit post-counter. A read can lag by up to 128 for about 12 cycles; core-et DV reads twice and takes the max.
- **Overflow.** There is no overflow interrupt.
- **Enable.** The neighbourhood ESR `pmu_ctrl` bit 0 disables the PMU clock (PRM:14705; M-mode ESR 0x01_C01N_0068 + shire<<22). It resets to 0 = enabled, and no firmware writes it.

**Minion events for `mhpmevent3-6`** (PRM Table 1-3, PRM:393-440; fw:et-common-libs/include/etsoc/drivers/pmu/pmu.h:129-158):

| # | Event | # | Event |
|---|---|---|---|
| 1 | CYCLES | 15 | TL_OPS (tensor-load request to L2) |
| 2/3 | RETIRED_INST0/1 | 16/17 | TS_INST / TS_OPS |
| 4/5 | BRANCHES0/1 (**broken**, Errata 1.12) | 18 | TFMA_WAIT_TENB (cycles FMA waits on L2 data) |
| 6/7 | DCACHE_ACCESS0/1 (loads/stores, not tensor/cacheops) | 19 | TIMA_OPS |
| 8/9 | DCACHE_MISSES0/1 | 20/21/22 | TXFMA_3216 / _32 / _INT ops |
| 10 | L2_MISS_REQ (L1 sent miss to L2) | 23/24/25 | TRANS / SHORT / MASK ops |
| 11 | L2_MISS_REQ_REJ (cycles L2 refused a miss) | 26/27/28 | TFMA / TREDUCE / TQUANT inst |
| 12/13 | L2_EVICT_REQ / _REJ | 29-31 | reserved |
| 14 | TL_INST | | |

**Neighbourhood events for `mhpmevent7-8`** (PRM Table 1-4, PRM:458-487; pmu.h:160-182):

| # | Event | # | Event |
|---|---|---|---|
| 1/2 | any minion ET-Link request sent / response received | 13/14 | I$ ET-Link req/rsp (I$ misses to L2) |
| 3/4/5 | coop-load req / inter-neigh coop req / rsp | 15/16 | I$→L1 SRAM req/rsp |
| 6/7 | coop-store req/rsp | 17/18 | PTW ET-Link req/rsp |
| 8/9 | minion→I$ req/rsp | 21 | ET-Link req pushed to intermediate FIFO |
| 10/11 | minion→PTW req/rsp | 22 | req pushed to any bank/UC FIFO |
| 12 | FLN message | 23 | ET-Link response received from SC/UC |

**Other hardware details:**
- **Latency by Little's law.** Events 1/2 and 21/22/23, counted over the same interval, give a per-neighbourhood request/response count. With cycles, that gives average ET-Link round-trip occupancy.
- **Read latency.** Switching which counter you read costs about 3 cycles (CET PMU_COUNTERS_READ_DELAY).

### 1.2 Privilege

**From the RTL (CET intpipe_csr_file.v:649-657, 1025-1031):**
- `mhpmevent3-8` (0x323-0x328) and `mhpmcounter3-8` (0xB03-0xB08) are **M-mode only**.
- `hpmcounter3-8` (0xC03-0xC08) are read-only shadows, readable in U-mode when both `mcounteren` and `scounteren` bits are set.

**What the firmware sets:**
- `mcounteren = 0x1F8` (fw:device-minion-runtime/src/MachineMinion/src/main.c:145).
- `scounteren = 0x1F8` (fw:device-minion-runtime/src/WorkerMinion/src/main.c:69).
- So **U-mode can read hpmcounter3-8, but it cannot choose events.**
- No syscall, launch flag, trace config or DM/MM command sets `mhpmevent`. `SYSCALL_SAMPLE_PMCS=309` and `SYSCALL_RESET_PMCS=310` are defined in syscall.h:11-12 but not handled (fw:WorkerMinion/src/syscall.c:29-78).

### 1.3 Default configuration (fw:MachineMinion/src/main.c:50-112, run once at boot in M-mode)

| Counter | Event | Who programs it | What a U-mode read means |
|---|---|---|---|
| hpmcounter3 | CYCLES | harts with `hartid%16` = 0 or 1 (minion 0 of each neighbourhood) only | minion clock cycles. The firmware uses it as the timestamp (`PMC_Get_Current_Cycles`, pmu.h:774). |
| hpmcounter4 | RETIRED_INST0 | every hart | thread-0 instructions retired, **summed over all 8 minions** of the neighbourhood |
| hpmcounter5 | RETIRED_INST1 | every hart | thread-1 instructions retired, summed over the neighbourhood |
| hpmcounter6 | L2_MISS_REQ | every hart | L1D miss requests to L2, summed over the 8 minions. With the neighbourhood otherwise idle, this is your minion's L1 miss count. |
| hpmcounter7 | MINION_ICACHE_REQ (8) | minion 0 | neighbourhood I$ requests |
| hpmcounter8 | ICACHE_ETLINK_REQ (13) | minion 0 | neighbourhood I$ misses sent to L2 |

**Reset behaviour:**
- hpmcounter4-8 are reset to 0 before **every launch** (`pre_kernel_setup` → `reset_minion_neigh_pmcs_all`; fw:MachineMinion/src/syscall.c:283-305, fw:et-common-libs/src/etsoc/drivers/pmu/pmu.c:84-97).
- hpmcounter3 is free-running.

**Errata when reading:**
- **Errata 1.23:** if both threads of a minion read different counters within 3 cycles, one of them can get wrong data. Use `HPM_SAFE_READ`: 4 back-to-back `csrr` inside one 16-byte-aligned half line (pmu.h:381-395). memhier already does this.
- **Errata 1.22:** do not use `csrrw`/`csrrs` on PMU CSRs (M-mode only anyway).

**Useful as it stands:**
- Cycles.
- Retired instructions.
- L1D misses for your neighbourhood.

**Needs a firmware change:**
- DCACHE_ACCESS/MISSES per thread.
- L2_MISS_REQ_REJ, a useful back-pressure signal.
- Neighbourhood ET-Link request/response counts.

---

## 2. Shire-cache (L2/L3/SCP) and NoC counters

### 2.1 Registers

There is one perf monitor per shire-cache bank: 4 banks × 33 shires. Each has a 40-bit cycle counter and two 40-bit event counters, P0 and P1, which can be preloaded and saturate. The registers are cache-bank ESR registers:

| Offset | Register | Address, bank `b`, shire `s` |
|---|---|---|
| 0x0B8 | `sc_perfmon_ctl_status` | 0x1_C030_0000 + (s<<22) + (b<<13) + off |
| 0x0C0 | `sc_perfmon_cyc_cntr` | same pattern |
| 0x0C8 / 0x0D0 | `sc_perfmon_p0_cntr` / `p1_cntr` | same pattern |
| 0x0D8 / 0x0E0 | `sc_perfmon_p0_qual` / `p1_qual` | same pattern |

**All of them are M-mode.** Sources: `ESR_CACHE_SC_PERFMON_*_PROT = PRV_M` (fw:et-common-libs/include/etsoc/isa/esr_defines.h:366-388); CET esr.csv:45-50; PRM:14960-14990. The PRM prints ctl_status at `0x01_0030_x0B8`, a user-mode address, but its Privilege column says M. That is a typo.

**ESR access rules:**
- ESRs need a 64-bit aligned `ld`/`sd`; no AMO, TensorOp or CacheOp (PRM Table 15-98 note 9).
- An access from too low a privilege is an access fault (PRM:14495-14520, §15.4).

**`ctl_status` bits** (fw:etsoc-hal/include/etsoc_hal/inc/etsoc_shire_cache_esr.h:2897-3206; SCspec §4.9):

| Bits | Field |
|---|---|
| 0-3 | cycle counter: start / reset / stop-on-overflow / irq |
| 4-7 | P0: s / r / o / i |
| 8 | P0 event (1) vs resource (0) |
| 16:9 | P0 mode |
| 17-21 | P1: the same, with 21 = P1 event |
| 29:22 | P1 mode |
| 30 | any-overflow-stops-all |
| 32-37 | status: active / overflow for C, P0, P1 |

**Event-mode qualifier (51 bits).** A request is counted when its opcode bit is set **and** its hit/miss, victim and victim-qword sub-fields match (fw:etsoc_shire_cache_esr.h:3351-3940; SCspec §4.9):

| Bits | Field |
|---|---|
| 1:0 | RBUF hit: bit0 L2, bit1 SCP (ORed with the rest) |
| 2 | MsgSend |
| 3 | tag bubble |
| 5:4 | TC_HIT_MISS: bit4 hit, bit5 miss |
| 8:6 | victim type: none / dirty / write-around |
| 13:9 | victim qwords |
| 25:14 | L2 ops: Read, Write, WriteAround, Lock, Unlock, UnlockInv, Flush, Evict, Prefetch, Atomic, Fill, Scrub |
| 35:26 | L3 ops: Read, Write, Flush, FlushWData, Evict, EvictWData, Prefetch, Atomic, Fill, Scrub |
| 41:36 | SCP ops: Read, Write, Fill, Scrub, Zero, Atomic |
| 50:42 | index cacheops |

Example qualifiers derived from the table:

| Qualifier | Value |
|---|---|
| L2 read miss | 0x7FE0 |
| L2 read hit | 0x7FD0 |
| L3 read miss | 0x4003FE0 |
| L3 read hit | 0x4003FD0 |
| RBUF L2 hits | 0x1 |

**Resource mode (e=0).**
- The qualifier holds `oper[7:0]` (0 = accumulate, 1 = count, 2 = max), `min[15:8]` and `max[23:16]`.
- Modes:
  - 0: P0 = active L2 reqq entries, P1 = active L3 reqq entries.
  - 1: busy flags.
  - 2: outstanding requests on to_l3 / to_sys.
  - 3: outstanding L2-originated requests on to_l3 / to_sys.
  - 4: outstanding L3 requests on to_sys / active coalescing buffers.
- Accumulate ÷ cycles = mean occupancy. Divided by the event count (Little's law), that is the **mean L2-miss or L3-miss latency per bank, measured in hardware**. This is the most direct decomposition tool on the chip, but it needs M-mode.
- Mode and qualifier encodings are from the core-et agent reading SCspec p.106. **Verify** them before trusting absolute values.

**Errata 3.3.** The cycle counter stops while the bank is idle because of clock gating. The firmware applies the workaround: it sets `sc_reqq_ctl` bit 22 (`clk_gate_disable[0]`) in `configure_sc_pmcs` (fw:et-common-libs/src/etsoc/drivers/pmu/pmu.c:19-21).

### 2.2 Firmware default at 353f20e

At boot, hart `%16==0` of each neighbourhood N programs **bank N** of its own shire (fw:MachineMinion/src/main.c:69-78; pmu.h:190-195):
- `ctl_status = 0x40280144`: P0/P1 in event mode 0, stop-on-overflow set, ao=1. It then starts the cycle counter, P0 and P1.
- **P0 qual = `0x257F5F17FF3`** ("all L2 reads"). Decoded: opcodes SCP{Read, Fill, Atomic}, L3{Read, Flush, FlushWData, Evict, EvictWData, Prefetch, Atomic, Fill}, L2{Read, WriteAround, Flush, Evict, Prefetch, Atomic, Fill}; hit **and** miss; all victim types and qwords; RBUF L2 and SCP hits. So P0 counts read-type requests handled by the bank, both as L2 and as the L3 slave, **without separating hits from misses**.
- **P1 qual = `0x2220881BFF0`** ("all writes"): SCP{Write, Atomic}, L3{Write, Atomic}, L2{Write, WriteAround, Atomic}; hit and miss.

The MM firmware's `statw` samples all of these about every `STATW_SAMPLING_INTERVAL` (fw:MasterMinion/src/workers/statw.c:207-225, statw.h:43). Each sample stops the counter, reads it and restarts it, and zeroes it only on overflow. Always use **deltas**.

### 2.3 What U-mode can do

**Read, but not configure.** `SYSCALL_PMC_SC_SAMPLE` = 9 is reachable from U-mode with `ecall`, `a0=9, a1=shire, a2=bank(0-3), a3=pmc` (0 = cycles, 1 = P0, 2 = P1). The path is WorkerMinion/src/syscall.c:69-71 → M-mode MachineMinion/src/syscall.c:130-131 → `sample_sc_pmcs`, which stops, reads and restarts (pmu.c:48-62).
- **Any shire is accepted**, so you can read the remote L3 home shire's bank.
- `bank` is not range-checked; pass only 0-3.
- The call costs two privilege transitions, a few hundred cycles, so bracket a whole experiment with it, not single loads.
- et-common-libs wraps it as `et_trace_pmc_sc()` (fw:et-common-libs/src/trace/trace_umode.c:19-23, trace/trace_umode.h:34-45).

**Configuring the qualifiers (hit vs miss, L3 vs L2, resource/occupancy mode) needs M-mode.** No syscall writes `p*_qual` or `ctl_status`.

**Other shire-cache ESRs, all M-mode** (esr_defines.h:282-404):
- `sc_l3_shire_swizzle_ctl`, `sc_reqq_ctl` (L2/L3 bypass, `num_l3_reqq_entries`, clock gating), `sc_pipe_ctl` (read-buffer enable `L2_RBUF_ENABLE` bit 36, one request per bank/sub-bank, RAM delay).
- `sc_idx_cop_sm_ctl_user` (reg 0x20) is PRV_U in the firmware header. The PRM says M. It is gated by `sc_pipe_ctl.IDX_COP_SM_CTL_USER_EN` (bit 42), which the firmware never sets, so treat it as unusable. The firmware's own `cache_ops_cb_drain` uses it anyway (cacheops-umode.h:391-414).
- The trace registers `sc_trace_*` are debug (PP=10), SP only.

### 2.4 NoC

- There are **no NoC performance counters** in the PRM, the firmware (only FlexNoC address maps in noc_reconfig_memshire.c) or core-et.
- NoC transit can only be inferred from the counters above:
  - neighbourhood events 1/2/21-23;
  - SC resource modes 2-4 (outstanding on to_l3 / to_sys);
  - latency differences, which memhier/nocbench already measure: about 12 cycles per mesh hop.

---

## 3. Memshire / DDR controller

### 3.1 Topology and type

- **Memshires.** 8 memshires, 4 west and 4 east. Each has 2 Synopsys uMCTL2 controllers, one per 16-bit LPDDR4X channel, for 16 channels in all (PRM:544-548, §1.5; fw:device-bootloaders/src/ServiceProcessorBL2/utils/mem_controller_utils.c:83-88, 604-607).
  - The datasheet instead says "two 16-bit PHYs sharing a single 32-bit controller" (DS:1349-1350). The firmware writes two controller instances per memshire, blk 0 and blk 1.
- **DRAM parts.** 4 LPDDR4X packages of 4 channels each on the V3 card (ET-PCIe-Dev-Card-V3.txt:32).
- **Per channel:** 1 rank, 8 banks, 2 KB page (10 column bits), 17 row bits. MR8 density 32 Gb/die = 16 Gb per channel, 2 GB per channel, 32 GB total (mem_controller_utils.c:943-1027; ranks/banks/page decoded from ADDRMAP).
- **ECC off:** `ecc=false`, ECCCFG0 `ecc_mode=0`.
- **Speed.** Firmware hard-codes the "933 MHz" configuration for every card, with a "TODO decide ddr_mode" comment (fw:device-bootloaders/src/ServiceProcessorBL2/driver/mem_controller.c:643-649).
  - 933 MHz is the controller/DFI clock. It runs 1:2 with the DRAM clock, so the DRAM clock is 1866 MHz and the data rate **3733 MT/s**, not the 4266 in the datasheet (MSTR=0x00080020, `memshire_ddr_init_functions.c:4536`, `DfiFreqRatio_p0=1` :768).
  - Peak is about 16 × 2 B × 3.733 GT/s = **119 GB/s**. memhier measured 76 GB/s.
  - `statw` uses the same 933 MHz to convert memshire cycles (statw.c:130-134).
- **Size flags.** The 4/8/32 GB flags are left at 0 while programming. The 32 GB card gets the generic table, and size is only detected from MR8 afterwards (mem_controller.c:208-210, 283-285, 389-420).

### 3.2 Timing as programmed (933 config, fw:etsoc-hal/src/memshire_ddr_init_functions.c:4407-4449)

One DFI clock is 1.071 ns; one tCK is half that. Decoding is by the research agent from uMCTL2 field definitions (`etsoc-hal/include/etsoc_hal/inc/DWC_ddr_umctl2.html`).

| Parameter | Register field | DFI clk | ns |
|---|---|---|---|
| tRCD | DRAMTMG4.t_rcd | 17 | 18.2 |
| tRP | DRAMTMG4.t_rp | 17 | 18.2 |
| tRAS(min) | DRAMTMG0.t_ras_min | 40 | 42.9 |
| tRC | DRAMTMG1.t_rc | 59 | 63.2 |
| RL / WL | DRAMTMG2 | 18 / 8 (= RL36/WL16 tCK; MR2=0x36, read-DBI on) | 19.3 / 8.6 |
| tCCD | DRAMTMG4.t_ccd | 4 (one BL16) | 4.3 |
| tRRD / tFAW | DRAMTMG4 / DRAMTMG0 | 10 / 38 | 10.7 / 40.7 |
| wr2pre / rd2pre | DRAMTMG0 / DRAMTMG1 | 30 / 8 | |
| tRFCab | RFSHTMG.t_rfc_min | 262 | 280.7 |
| tREFI | RFSHTMG.t_rfc_nom = 113, x1_sel = 1 | 3616 if ×32 | ~3.87 µs |
| tXSR | DRAMTMG14 | 269 | 288 |

**Registers as read (DRAMTMG0-4):**
- DRAMTMG0 = 0x1e261f28
- DRAMTMG1 = 0x0007083b
- DRAMTMG2 = 0x08121316
- DRAMTMG4 = 0x11040a11

**Other settings:**
- MR1 = 0x64 (nWR=34). MR3 = 0xF1: read and write DBI on.
- `post_train_update_regs` adds training-derived increments to `DRAMTMG2.rd2wr` and `DFITMG1` per channel (mem_controller_utils.c:811-923). The card's values are therefore a bit larger than the table.

**Refresh:**
- All-bank refresh (RFSHCTL0=0x00210000, `per_bank_refresh=0`).
- The `t_rfc_nom_x1_sel=1` read literally gives 121 ns < tRFC, which is impossible. The only sensible reading is ×32, i.e. 3.87 µs.
- A 280 ns all-bank refresh every 3.9 µs blocks a channel about 7% of the time. It will show up as a tail of roughly +280 ns on single-load DRAM latency.

**Power and background activity:**
- PWRCTL=0: no power-down or self-refresh ("disable self-refresh for performance", :5459).
- No automatic ZQ (ZQCTL0.dis_auto_zq=1).
- The DFI controller-update is automatic every 64-255 × 1024 clocks. It can cause rare latency blips.

**Rough DRAM-side budget for a closed-bank read:** tRCD + RL + burst (2 × BL16 = 64 B) ≈ 18 + 19 + 8.6 ≈ **46 ns** at the pins. That is out of the ~440 ns measured load-to-use. So roughly 390 ns is NoC, shire cache (L2 miss + L3 miss handling), memshire queues and PHY.

Adjustments:
- A row conflict adds tRP ≈ 18 ns.
- A row hit saves tRCD ≈ 18 ns.

### 3.3 Page policy and scheduling

- **Open page.** SCHED=0x00a01f01 (pageclose=0), SCHED1.pageclose_timer=0, PCCFG=0 (no pagematch).
- **Port priorities.** PCFGR/W_0 = 0x100f and PCFGR/W_1 = 0x1008: aging on, priority 15 and 8.
- **No auto-precharge.** `ddrc_main_ctl` (read/write auto-precharge bits; PRM:15515) stays at 0, because `config_auto_precharge=0` (mem_controller.c:245).
- **Nobody can change this at runtime.** DDR controller registers are service-processor only.

### 3.4 Physical address mapping

These hold for the Minion-visible DRAM region `0x80_0000_0000 + offset` (PRM:17135-17150, §15.6). Minions can only reach the "Low" view.

- **Memshire and controller: PA[8:6] and PA[9].**
  - Source: the comment in fw:device-minion-runtime/tools/zebumem.c:68-72, 120-121.
  - Corroborated by the NoC DRAM address-mask field 0x1c0 = PA[8:6] (fw:etsoc-hal/src/noc_reconfig_memshire.c:610) and by the `ms_mem_ctl` reduced-memshire decode (noc_configuration.c:294-313). Those tables are not used at the default boot, so the hardware default applies.
  - Consequences:
    - Consecutive 64 B lines rotate over the 8 memshires.
    - PA[9] alternates the two channels every 512 B.
    - A given channel sees every 1 KB.
- **Inside the controller, 4 bits (PA[9:6]) are removed.**
  - ADDRMAP1..7 = 0x030303, 0x03000000, 0x03030303, 0x1f1f, 0x07070707, 0x07070707, 0xf07 (memshire_ddr_init_functions.c:4578-4656).
  - Decoded from HIF: col[4:0] = HIF0-4, bank[2:0] = HIF5-7, col[9:5] = HIF8-12, row[16:0] = HIF13-29.
  - In PA terms (inferred):

    | DRAM field | PA bits |
    |---|---|
    | col[4:0] | PA[5:1] (a 64 B line is 2 BL16 bursts in one row) |
    | bank | PA[12:10] |
    | col[9:5] | PA[17:13] |
    | row | PA[34:18] |

  - A 256 KB aligned block therefore touches one row in each of the 128 channel-banks.
  - **Verify on silicon** with a same-channel stride sweep: 1 KB steps should hit different banks, 8 KB steps the same bank and row, 256 KB steps the same bank and a different row.
- **L3 home slice** (CET esr_cache_bank.v:89-103, default "swizzle0"):
  - home shire = PA[10:6], i.e. 32 shires with 64 B interleave.
  - L3 bank = PA[12:11], sub-bank = PA[14:13].
  - `sc_l3_shire_swizzle_ctl` is left at reset 0 (only the unused `reconfig_minion_shire` path writes it, noc_configuration.c:316-347).
  - These are **virtual** shire IDs; see `NOC_Remap_Shires` (noc_configuration.c:423-431) for spare-shire remapping.
- **L2 (local)** (SCspec §1): bank = PA[7:6], sub-bank = PA[9:8], set from PA[10+].
- **Caveat: VA vs PA.** Kernels on 353f20e run with translation off (bare) as far as memhier assumes, so kernel VAs equal PAs. mallocDevice returns 0x80_xxxx_xxxx addresses. **Verify** before relying on exact bits.

### 3.5 DDR controller performance counters

**Registers.** Each memshire has one monitor with a cycle counter and two event counters, P0 and P1, all 40-bit:

| Offset | Register |
|---|---|
| 0x280 | `ddrc_perfmon_ctl_status` |
| 0x288 | `cyc_cntr` |
| 0x290 / 0x298 | `p0_cntr` / `p1_cntr` |
| 0x2A0 / 0x2A8 | `p0_qual` / `p1_qual` (64-bit) |
| 0x2B0 / 0x2B8 | `p0_qual2` / `p1_qual2` (min/max) |

The PRM gives them at 0x01_Bxy0_02xx and calls them SP-only (PRM:15565-15583). The firmware accesses them as **M-mode** ESRs in the memshire ESR space: `ESR_DDRC(0xE8+ms, …)`, PROT=PRV_M (esr_defines.h:195-198, 851-881). Either way, U-mode cannot touch them directly.

**`ctl_status` layout** is the same as the shire cache's (etsoc_ddr_controller.h:1629-2028). The mode byte is op[7:6], type[5:0]. Qualifier formats (CET memshire_defines.vh:215-250):

| Format | Fields |
|---|---|
| MCOP | uMCTL2 op bits cmd[14:0]: rd, wr, mwr, **activate, precharge (for rd/wr vs other), refresh, crit/spec refresh**, ZQ, rd_activate, self-refresh/powerdown; mc0/mc1 select; bank[27:20] |
| MCMISC | rd/wr turnaround, WAW/RAW/WAR hazards, write-combine |
| MCDATA | rd/wr data beats |
| MESHCNT | incoming NoC reads/writes by source (IO/PShire/minion shires), exact source, QoS, and an **address filter** (base/mask) |
| MESHOUT | outgoing responses |

The perfmon interface carries the uMCTL2 `perf_op_is_{activate,precharge,rd,wr,refresh,…}` and `perf_hif_*`, `raq/waq push/pop` signals for both controllers (CET dv/soc/memshire/evl_memshire_perfmon_itf.sv:42-174). The numeric type values that select each format, and the cmd-bit order, are **not** in any source we have; they are in the missing "Memory Shire Specification §5.4.22-29".

**This is the counter for DRAM activates, precharges, page hits/misses and refresh**, if the encodings can be found or reverse-engineered from M-mode.

**Firmware default** (fw:MachineMinion/src/main.c:81-93; pmu.h:199-239):
- Shire 0, neighbourhood 3, hart 14 runs `configure_ms_pmcs(ms, ctl=0xC80644, p0_qual=0x1FD, p1_qual=0x1FE)` for all 8 memshires.
- `0xC80644` means P0/P1 mode 3, which matches the MESHCNT format, plus stop-on-overflow.
- P0 = mesh **reads** from all sources; P1 = mesh **writes**.
- These counters feed the "DDR BW" figure through `statw` and `DM_CMD_GET_MM_STATS` (61), shown by et-top.

**From U-mode:**
- `SYSCALL_PMC_MS_SAMPLE` = 10: `a1=ms (0-7)`, `a2=pmc` (0 = cycles at 933 MHz, 1 = reads, 2 = writes) (WorkerMinion/src/syscall.c:72-73 → pmu.c:64-81). Each call stops, reads and restarts. `et_trace_pmc_ms()` wraps it.
- With PA[8:6] selecting the memshire, a single-line experiment can confirm which memshire served it by looking at the delta in that memshire's read count. That is a direct check of the §3.4 mapping.
- Nothing can reprogram the qualifiers: no syscall or DM command. The status-monitor trace masks (`ddrc_debug_sigs_mask*`, `ddrc_trace_ctl`) are never programmed.

---

## 4. Timestamped tracing

**U-mode trace buffer.**
- Set it up with `KernelLaunchOptions` `userTraceConfig` → `CMD_FLAGS_COMPUTE_KERNEL_TRACE_ENABLE` → `KERNEL_LAUNCH_FLAGS_COMPUTE_KERNEL_TRACE_ENABLE`. The firmware then sets up per-hart buffers (fw:esperanto-tools-libs/src/KernelLaunch.cpp:128-141; fw:MasterMinion/src/workers/kw.c:740-768; fw:WorkerMinion/src/kernel.c:501, 702).
- Every entry is stamped with `hpmcounter3`, the cycle counter (`ET_TRACE_GET_TIMESTAMP`, trace_umode.c:39).
- Kernel-side calls (fw:et-common-libs/include/trace/trace_umode.h:22-80, et-trace/include/et-trace/encoder.h:950-1000):
  - `et_trace_pmc_compute` logs hpmcounter3-8.
  - `et_trace_pmc_sc` logs this shire and neighbourhood's bank counters through syscall 9.
  - `et_trace_pmc_ms(ms)` logs through syscall 10.
  - Also `et_trace_user_profile_event` and `et_printf`.
- **The trace adds no timing resolution** beyond reading hpmcounter3 yourself. It is only a convenient sink, and each entry costs cache traffic.
- **There is no hardware sampling.** The PMU has no overflow interrupt and the trace is software-driven.

**MM trace / statw.** Periodic device-level SC/MS bandwidth samples only. Too coarse for per-access work.

**Hardware address trace.**
- `sc_trace_address_enable/value/ctl` in the shire cache and `ddrc_trace_ctl` / `ddrc_debug_sigs_mask*` in the memshire feed the UltraSoC debug fabric (status monitor: 200 memory-controller signals, 2 counters; DS:1374-1382).
- They are debug/SP privilege and not reachable from the runtime.

---

## 5. Latency-relevant structure of L1 → L2 → L3 → memshire

**L1D:**
- 4 KB, 16 sets × 4 ways × 64 B, set = PA[9:6].
- The firmware puts it in split+scratchpad mode before every launch. Each hart then gets 2 sets = 512 B (fw:MachineMinion/src/syscall.c:348-420; PRM Table 8.4).
- **2 miss handlers per minion,** so at most 2 outstanding cacheable line misses. A second access to the same line merges (CET dcache_defines.vh:79).
- Tensor loads keep up to 4 L2 transfers in flight.
- There is no prefetcher.

**Neighbourhood → shire-cache crossbar** (Neighborhood-MAS §4.3-4.4):
- At least 6 cycles for a request.
- 3-deep bank FIFOs and a 2-deep intermediate FIFO. Neighbourhood event 21/22 counts pushes into these.
- The fill FIFO is 4 entries (at least 2 cycles), plus a 2-cycle VC input.

**Shire cache (SCspec §1-2; esr_cache_bank.v; see §2.1 for counters):**
- 4 banks × 4 sub-banks; 4-way, true LRU; write-back, write-allocate; not coherent.
- Per bank:
  - 64-entry request queue. These are the MSHR-equivalents; each entry lives through miss, fill and victim.
  - Up to 21 of the 64 entries are reserved for L3-slave requests (`num_l3_reqq_entries` default).
  - 8-entry read buffer (RBUF).
  - 32-entry coalescing buffer for write-arounds.
- L3-slave requests take priority over local L2 requests unless `l3_yield` is set. See Errata 3.2 for sub-bank starvation.
- RAM delay is 2 cycles by default, so a sub-bank accepts one request every 2 cycles.
- Idle latencies from SCspec Table 1, in shire clocks, including the crossbars:

  | Access | Latency |
  |---|---|
  | RBUF hit | 10 |
  | L2 hit | 21 |
  | L2 miss | 34 + NoC + L3 |
  | L3 hit (at the slave) | 30 |
  | L3 miss | 42 + NoC + DRAM |

  The measured load-to-use numbers were RBUF 36, L2 47, L3 169 cycles. The ~26-cycle difference is the minion pipeline, L1 miss and neighbourhood path.

**Request path:**
1. An L1 miss sends ET-Link `Read_L2` to the local bank, chosen by PA[7:6].
2. On an L2 miss, the bank sends `Read_L3` over **to_l3** (the mesh, 4 ports) to the home shire's L3 slave, chosen by PA[10:6]. The data returns directly to the neighbourhood before the fill; the fill may create a victim writeback.
3. On an L3 miss, the slave sends a request over **to_sys** (1 port) to the memshire chosen by PA[8:6]. The NoC delivers it to the memshire AXI port: 512-bit, up to 32 GB/s per memshire (DS:1360-1372).
4. The uMCTL2 then does ACT / RD / PRE under the open-page policy.

`…G` (global) loads bypass L2 and go straight to L3 as `Read_L3` (CET dcache_miss_handler.v:492-511). That lets a kernel time L3 without evicting L2.

**A decomposition you can build from U-mode today:**

| Probe | Measures |
|---|---|
| RBUF | read the same line again right after an L1 evict to L2 |
| L2 | EvictVA dst=L2 |
| L3 | EvictVA dst=L3, or an `flw.g`-type global load |
| DRAM | EvictVA dst=MEM |
| NoC hops | pick PAs whose PA[10:6] home shire is at a known mesh distance |
| DRAM row hit / closed / conflict | vary the PA bits in §3.4 on one channel |
| Refresh | the latency histogram tail |

---

## 6. Flushing and evicting from U-mode

**Directly from U-mode** (PRM Table 8.1, PRM:5906-5917; wrappers in fw:et-common-libs/include/etsoc/isa/cacheops-umode.h:161-322):

| Op | CSR | Notes |
|---|---|---|
| EvictVA | 0x89F | dst L2/L3/MEM, 1-16 lines, stride in x31 |
| FlushVA | 0x8BF | write back but keep a clean copy |
| PrefetchVA | 0x81F | to L1/L2/L3; wait with TensorWait 4/5 via `x31[0]` id |
| LockVA / UnlockVA | 0x8DF / 0x8FF | |
| `ucache_control` | 0x810 | CacheOp rate/max; ScpEnable from thread 0 only |

EvictSW / FlushSW / LockSW / UnlockSW (0x7F9-0x7FF) are M-mode only.

**U-mode syscalls** (`ecall`, a0=number). The worker's S-mode trap handler passes **every** U-mode ecall number to `syscall_handler`; there is no filtering by range (fw:WorkerMinion/src/trap_handler.S:80-86; syscall.c:29-78). Numbers from fw:et-common-libs/include/etsoc/isa/syscall.h:9-27.

| # | Syscall | Effect |
|---|---|---|
| 1 / 2 | EVICT_SW / FLUSH_SW | M-mode set/way evict/flush of your own L1 |
| 5 | CACHE_OPS_INVALIDATE | I$ / TLB invalidate |
| 6 | EVICT_L1 (use_tmask, dest) | whole L1 of the calling minion to a level |
| 7 | SHIRE_CACHE_BANK_OP (shire, bank, op) | index cacheop on **any shire's bank**: L2_FLUSH / L2_EVICT / L3_FLUSH / L3_EVICT / CB_INV (MachineMinion/src/syscall.c:534-548). Evicting the whole L2 or the L3 slice of one bank this way is much cheaper than line-by-line work for large sets. |
| 11 | EVICT_WHOLE_L1_L2 | whole local L1 and the entire shire L2 |
| 301 | CACHE_CONTROL (d1_split, scp_en) | Reaches `set_l1_cache_control` in M-mode, so a kernel **can** switch its L1 back to 4 KB shared mode after launch (MachineMinion/src/syscall.c:85-86, 580-640). This contradicts the memhier README's "cannot switch back". **Verify**; the next launch's `init_l1` restores split+SCP. |
| 302 | FLUSH_L3 | flush this shire's L3 slice |
| 9 / 10 | PMC_SC_SAMPLE / PMC_MS_SAMPLE | see §2.3 and §3.5 |

**Launch option.** `flushL3=true` in `kernelLaunch(…, barrier, flushL3)` (IRuntime.h:135-148) sets `CMD_FLAGS_KERNEL_LAUNCH_FLUSH_L3` → `KERNEL_LAUNCH_FLAGS_EVICT_L3_BEFORE_LAUNCH`. Hart 0 of each of shires 0-31 in the launch then evicts its L3 slice before the kernel starts (kw.c:881-885; WorkerMinion/src/kernel.c:552-566). The whole L3 is only evicted if all 32 shires take part.

---

## 7. Summary: what is available where

| Capability | U-mode on 353f20e | Needs |
|---|---|---|
| Cycle count (hpmcounter3) | read | – |
| Retired instructions, L1D→L2 misses (neighbourhood sum), I$ requests/misses | read hpmcounter4-8 (reset each launch) | – |
| Choose minion or neighbourhood events (DCACHE_MISSES, L2_MISS_REQ_REJ, ET-Link req/rsp) | no | M-mode firmware change (`mm_setup_default_pmcs`) or a new syscall |
| Shire-cache bank read/write request counts (hit+miss combined) + bank cycles, any shire | read via syscall 9 | – |
| Shire-cache hit/miss split, L3-only, RBUF hits, occupancy (Little's law miss latency) | no | M-mode: write `sc_perfmon_p*_qual` / `ctl_status` |
| Memshire mesh read/write counts + 933 MHz cycles, any memshire | read via syscall 10 | – |
| DRAM activates / precharges / refresh / hazards / address-filtered counts | no | M-mode, plus the missing mode/cmd encodings |
| DDR timings, page policy, refresh mode | fixed (open page, all-bank refresh, 3733 MT/s) | SP bootloader change |
| Evict/flush/prefetch one line to L2/L3/MEM | EvictVA/FlushVA/PrefetchVA + `tensor_wait 6` | – |
| Evict a whole L2 or L3 bank, any shire | syscall 7 / 11 / 302; flushL3 launch option | – |
| NoC counters | none exist | – |

**Smallest firmware change with the biggest payoff.** Add a U-mode syscall that writes `mhpmevent3-8` for the calling hart and `sc_perfmon_{ctl_status,p0_qual,p1_qual}` for a given shire and bank. It would be a few lines in MachineMinion/src/syscall.c and WorkerMinion/src/syscall.c, reusing `pmu_core_event_configure` and `configure_sc_pmcs`. That alone gives hit/miss per level and hardware-measured mean miss latency per bank.
