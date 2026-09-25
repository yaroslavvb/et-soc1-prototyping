# Earlier findings: memory, counters, and the limits of observability

[← Findings index](README.md) · published as [Anatomy of a memory access](https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy) (A1) and
[Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability) (A2, first edition) · numbers and sources:
[05-claims.md](05-claims.md)

**Sources:** E1, E2, E3, E4 (this line of work, 19–20 September), R4 (the 18 September reports that preceded
it).

These predate the power work but are the reason the later experiments could be trusted: they establish what
the card's instruments actually report.

---

## One memory access, taken apart (E1 → A1)

Cycles at 600 MHz, load-to-use, one load in flight. Found by using `evict_va` (CSR 0x89f) to place a line at a
chosen level and timing a single load. The levels, shires and mesh hops are defined in [README.md](README.md#terms).

| Stage | Cost |
|---|---|
| L1 hit | 5 cycles |
| L2 hit | 48 cycles from the array; 37 when the line is still in the bank's 8-entry read buffer |
| L3 hit | **110 + 12 × hops**(requester → home shire); home shire = PA[10:6] |
| DRAM leg past L3 | **91 + 12 × hops**(home → memory shire); memory shire = PA[8:6]. Of the 91, about 25 are the DRAM chip (activate 11 + read and burst 14; the rows had closed) and about 66 the memory shire |
| Open-row hit | saves 11 cycles (tRCD) |
| Same bank, different row | +40 cycles |
| Refresh | every 2,325 cycles = 3.88 µs; a load caught in one waits up to 210 cycles and the open row closes |

Address decode: rows PA[18+], bank PA[12:10], column PA[17:13]. The L3 map was verified over 1,500 addresses,
all within ±4 cycles of the model but two (median of three loads per line; 1,309 of 1,500 within ±2).

Energy per load (one 8-byte `ld`; below L1 each moves a 64 B line), above idle, 1,024 minions: **L1 46 pJ, L2
183 pJ, L3 local 541 pJ (+59 per hop), DRAM 5.1 nJ** (67% off the metered rails, mostly DDR; 18% on the mesh).
These come from the service processor's rail trace, whose rise above idle is 14–20% smaller than the host
board-power log's. The energy manual re-measured the levels at 600 MHz on both cards (E29): L1 0.77, L2 2.51, L3 10.5
(lines homed across the whole chip, so several mesh hops on average, not the local slice) and DRAM 122 [117–129] pJ/B.
Per 64 B that is about 49 pJ read from L1 (not comparable with the 46 pJ above, which is one 8-byte `ld` and its loop, moving no line),
and 161 pJ, 0.67 nJ and **7.8 nJ** per line from L2, L3 and DRAM. For DRAM, quote the E29 figure.

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
| Energy | **133 µJ** (1 mW × 133 ms on a rail, behind the PMIC's ~1 s running average); one bit flip is ~10⁻¹⁶ J |
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

The second edition (23–24 September) made A2 the hub of every measurement report; its meter chain, unmetered
remainder and improvement ladder are in [19-observability-and-the-unmetered.md](19-observability-and-the-unmetered.md).

## From the 18 September reports (R4, different sessions, one on a different card)

Baselines this work quotes but did not re-measure:

- **Matmul efficiency** (aifoundry2, `kernels/mmbench`): fp32 9.5 TFLOP/s at 168 GFLOP/s per W; fp16
  19.0 TFLOP/s at 321 GFLOP/s per W; int8 71.8 TOP/s at 1,162 GOP/s per W.
- **Sparsity** (aifoundry3 — *a different card, do not mix its watts with this one's*): the tensor unit's
  zero-skip saves **energy but not cycles** — 546 cycles per fp32 op at any sparsity — and board power above
  idle scales with the nonzero multiplies. This is the direct ancestor of
  [10-data-dependent-power.md](10-data-dependent-power.md). The PRM's fp16 zero-skip rule is a documentation
  bug; silicon computes the correct sum.
- **On-chip communication:** 20 ns per mesh hop in both directions at any clock (12 cycles at 600 MHz); inside
  a shire 68 cycles on reduction-tree edges and 114 elsewhere; a 1,024-minion allreduce in 2.3 µs; energy per byte
  0.8 pJ on tree edges, 2.3 pJ within a shire, ~10 + 1.9 pJ per hop across the mesh, busy cores included
  (re-measured in E29).
- **Memory hierarchy:** per-level latency, bandwidth and energy per byte against the A100. Since 24 September its
  bandwidth column uses only the launches that ran at 600 MHz (L2 2.45 TB/s, 128 B per shire-cycle) and its energy
  column the energy manual's §4 (E29). The 18 September averages (2.80 TB/s, "about 144 B/cycle", 148 pJ/B for DRAM,
  DRAM latency ~440 ns) are kept on its Versions line; the corrections are in [05-claims.md](05-claims.md), "Two
  corrections".

## Related

- [10-data-dependent-power.md](10-data-dependent-power.md): the power work these instruments made possible.
- [11-thermal-model.md](11-thermal-model.md): the RTL flip counts, joined to joules measured on the card.
- [19-observability-and-the-unmetered.md](19-observability-and-the-unmetered.md): the observability report's
  second edition.
- [14-card-behaviour.md](14-card-behaviour.md): the traps, including the counter bug.
