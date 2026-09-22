# Earlier findings: memory, counters, and the limits of observability

**Sources:** E1, E2, E3, E4 (this line of work, 19–20 September), R4 (the 18 September reports that preceded
it). Published as A1 and A2.

These predate the power work but are the reason the later experiments could be trusted: they establish what
the card's instruments actually report.

---

## One memory access, taken apart (E1 → A1)

Cycles at 600 MHz, load-to-use, one load in flight. Found by using `evict_va` (CSR 0x89f) to place a line at a
chosen level and timing a single load.

| Stage | Cost |
|---|---|
| L1 hit | 5 cycles |
| L2 hit | 48 cycles (37 of them the bank's read buffer) |
| L3 hit | **110 + 12 × hops**(requester → home shire); home shire = PA[10:6] |
| DRAM leg past L3 | **91 + 12 × hops**(home → memory shire); memory shire = PA[8:6] |
| Open-row hit | saves 11 cycles (tRCD) |
| Same bank, different row | +40 cycles |
| Refresh | every 2,325 cycles = 3.88 µs; a load caught in one waits up to 210 cycles and the open row closes |

Address decode: rows PA[18+], bank PA[12:10], column PA[17:13]. The L3 map was verified over 1,500 addresses,
all within ±2 cycles of the model but two.

Energy per 64 B load, above idle, 1,024 minions: **L1 46 pJ, L2 183 pJ, L3 local 541 pJ (+59 per hop), DRAM
5.1 nJ** (67% on the DDR side, 18% on the mesh).

## The cycle counter is wrong, and the RTL says why (E2)

`hpmcounter3` **reads 128 short whenever its low 7 bits are 0–10**. Simulating the original `neigh_pmu.v`
under Verilator reproduces it exactly: each counter is a 7-bit pre-counter plus a 57-bit post-counter, twelve
counters share **one** adder that folds pre-counter overflows into the post-counters round-robin, and a read
ignores the pending overflow bit. After every wrap the value is short until the adder comes round — 12 cycles
in simulation, 11 on the card.

This is the clearest example in the whole project of the open RTL paying for itself: a silicon measurement
explained by a flip-flop-level view of the design.

## Limits of observability (A2)

How far down you can see on this card, from a user account:

| | Finest granularity |
|---|---|
| Time | **1 cycle** (`hpmcounter3`, corrected) |
| Architectural state | **64 bits** — one register, CSR or memory word of a halted hart, per management round trip |
| Energy | **133 µJ** (1 mW × 133 ms on a rail); one bit flip is ~10⁻¹⁶ J |
| Every net, every cycle | **RTL simulation only** |

**Can individual bit flips be tracked on silicon? No, and no firmware change would fix it.** Nothing on the
die counts toggles. The PMU counts operations, the cache and memory monitors count requests, and the power
path resolves 1 mW over 133 ms — twelve orders of magnitude above one node toggle. ECC covers only L2/L3/
scratchpad SRAM and the instruction cache (not L1 data, not the register files), DRAM ECC is compiled off, and
at this firmware the SP never enables the interrupt sources, so the counters read 0 forever. The UltraSoC
debug fabric is on the die but its clock is gated at boot and no open tool configures it.

**In simulation, yes, twice over:** `sys_emu -l` prints every architectural write of every instruction, and
the RTL bench dumps every net and flop every cycle. That is exactly the gap this project later exploited — the
flip counts in [11-thermal-model.md](11-thermal-model.md) come from RTL, and the joules come from the card.

Two tools came out of the follow-up (E3, E4): a device flame graph
(`workloads/traceprof` + `scripts/trace-flamegraph.py`) and a PMU event-select syscall that works in `sys_emu`
but **cannot be run on the card** without a signed firmware image.

## From the 18 September reports (R4, different sessions, one on a different card)

Baselines this work quotes but did not re-measure:

- **Matmul efficiency** (aifoundry2, `kernels/mmbench`): fp32 9.5 TFLOP/s at 168 GFLOP/s per W; fp16
  19.0 TFLOP/s at 321 GFLOP/s per W; int8 71.8 TOP/s at 1,162 GOP/s per W.
- **Sparsity** (aifoundry3 — *a different card, do not mix its watts with this one's*): the tensor unit's
  zero-skip saves **energy but not cycles** — 546 cycles per fp32 op at any sparsity — and board power above
  idle scales with the nonzero multiplies. This is the direct ancestor of
  [10-data-dependent-power.md](10-data-dependent-power.md). The PRM's fp16 zero-skip rule is a documentation
  bug; silicon computes the correct sum.
- **On-chip communication:** 12–16 cycles per mesh hop, not symmetric between shire pairs; energy per byte
  0.8 pJ on tree edges, 2.3 pJ within a shire, ~10 pJ + 1.9 pJ per hop across the mesh.
- **Memory hierarchy:** per-level latency, bandwidth and energy per byte.
