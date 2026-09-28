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
| L3 hit | **110 + 12 × hops**(requester → home shire); home shire = PA[10:6]; 110.5–110.6 + 11.99 × hops on each of three cards (E35) |
| DRAM leg past L3 | **91 + 12 × hops**(home → memory shire); memory shire = PA[8:6]; the constant reads 90–91 pass by pass on three cards (E35). Of the 91, about 28 are the DRAM chip (activate 11, the 19.3 ns read latency and two BL16 bursts, 17 cycles together; the rows had closed) and at most ~63 the memory shire (at most: moving the memory shires a hop further out moves 12 cycles into the mesh legs) |
| Open-row hit | saves 11 cycles (tRCD); 11.0–11.6 on three cards |
| Same bank, different row | +38 cycles (38.5; 36.9, 37.4 and 36.5 on aifoundry2, aifoundry3 and aifoundry1's card 1) |
| Refresh | every 2,325 cycles = 3.88 µs (in every pass on three cards); a load caught in one waits up to 208 cycles (208–209 on three cards) and the open row closes |

Address decode: rows PA[18+], bank PA[12:10], column PA[17:13]. The L3 map was verified over 1,500 addresses,
all within ±4 cycles of the model but two (median of three loads per line; 1,309 of 1,500 within ±2).

Energy per load (one 8-byte `ld`; below L1 each moves a 64 B line), above idle, 1,024 minions: **L1 46 pJ, L2
183 pJ, L3 local 541 pJ (+59 per hop), DRAM 5.1 nJ** (67% off the metered rails, mostly DDR; 18% on the mesh).
These come from the service processor's rail trace, whose rise above idle is 14–20% smaller than the host
board-power log's (5.1 nJ per DRAM load on the trace, 5.9 on the log). The energy manual re-measured the levels at
600 MHz on three cards (E43, six passes each; `manual.json` `.reruns.levels_pj_per_byte`): L1 0.75, L2 3.11, L3 14.7
(lines homed across the whole chip, so several mesh hops on average, not the local slice) and DRAM 114.6
[89.0–141.3] pJ/B, with about 68–70% of a DRAM tensor load's energy on no metered rail on all three cards. Per 64 B
that is about 48 pJ read from L1 (not comparable with the 46 pJ above, which is one 8-byte `ld` and its loop, moving
no line), and 199 pJ, 0.94 nJ and **7.3 nJ** per line from L2, L3 and DRAM. For DRAM, quote the E43 figure (E29's of
23 September, two cards: L1 0.77, L2 2.51, L3 10.5, DRAM 122 [117–129] pJ/B, 7.8 nJ per line).

## The cycle counter is wrong, and the RTL says why (E2)

`hpmcounter3` **reads 128 short whenever its low 7 bits are 0–10**. Simulating the original `neigh_pmu.v`
under Verilator reproduces it exactly: each counter is a 7-bit pre-counter plus a 57-bit post-counter, twelve
counters share **one** adder that folds pre-counter overflows into the post-counters round-robin, and a read
ignores the pending overflow bit. After every wrap the value is short until the adder comes round — 12 cycles
in simulation; on the card the window covered at least 0–10 and 0–9 in two launches (19 September). In the three-card
check (E35) every back-to-back pair still differed by 10, 138 or −118 cycles, but no single window fitted every pair
in 11 of the 15 launches of the raw-pair probe (all five on aifoundry3): the mechanism holds, the fixed window does
not (MEM-R1 failed on all three cards). `fixcyc()` still leaves about 1 timed interval in 70 ±128 off (0–5% per
launch on the three cards): drop those, or take the median of repeated loads.

This is the clearest example in the whole project of the open RTL paying for itself: a silicon measurement
explained by a flip-flop-level view of the design.

## Limits of observability (A2)

How far down you can see on this card, from a user account:

| | Finest granularity |
|---|---|
| Time | **1 cycle** (`hpmcounter3`, corrected) |
| Architectural state | **64 bits** — one register, CSR or memory word of a halted hart, per management round trip |
| Energy | **133 µJ** (1 mW × 133 ms on a rail on aifoundry2, behind the PMIC's running average, τ ≈ 1.2 s; aifoundry3's readings change only every ~250 ms); one bit flip is ~10⁻¹⁶ J |
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

Baselines from 18 September, each re-measured on three cards in the version-3 check (26 September):

- **Matmul efficiency** (aifoundry2, `kernels/mmbench`): fp32 9.5 TFLOP/s at 168 GFLOP/s per W; fp16
  19.0 TFLOP/s at 321 GFLOP/s per W; int8 71.8 TOP/s at 1,162 GOP/s per W. The rates are the same on each of the
  three cards (E37); the efficiency depends on each card's idle and die temperature: 138–189, 270–370 and
  958–1,377 per W on the three cards.
- **Sparsity** (aifoundry3 — *a different card, do not mix its watts with this one's*): the tensor unit's
  zero-skip saves **energy but not cycles** — 546 cycles per fp32 op at any sparsity, on each of three cards
  (E39) — and board power above idle falls by 86–93% as A goes from dense to all zeros (86% in the first run). This is the direct ancestor of
  [10-data-dependent-power.md](10-data-dependent-power.md). The PRM's fp16 zero-skip rule is a documentation
  bug; silicon computes the correct sum.
- **On-chip communication:** 20 ns per mesh hop in both directions at any clock (12 cycles at 600 MHz); inside
  a shire 68 cycles on reduction-tree edges and 114 elsewhere; a 1,024-minion allreduce in 2.3 µs; energy per byte,
  busy cores included, as re-measured on three cards on 26 September (E43, six passes each; `manual.json`
  `.reruns.rings_pj_per_byte`): 0.69 pJ on pairs, 2.2 in a neighbourhood or a shire ring, 9.2 + 1.75 pJ per mean
  hop across the mesh (9.1 + 1.78, 8.0 + 1.73 and 10.4 + 1.74 on aifoundry2, aifoundry3 and aifoundry1's card 1;
  the on-chip communication page). E29's two-card values of 23 September (0.67, 2.1, 9.3 + 1.7, r² 0.95) and the
  18 September ones (0.8, 2.3 and ~10 + 1.9) are superseded (E34).
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
