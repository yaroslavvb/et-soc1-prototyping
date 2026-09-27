# 4. Bytes through the memory hierarchy

Energy per byte moved, above idle, at 600 MHz. Zeros and random data, because the data is a large part of the cost at every level: random data costs 1.4–2.1× what zeros cost on the paths of 4.1.

Every entry is **mean** [lo–hi]: the mean over every pass on every card, and the full range those passes spanned. "a2", "a3" and "a1c1" are aifoundry2, aifoundry3 and aifoundry1's card 1, each as its own mean ± its pass-to-pass standard error.

## 4.1 Reads and writes, measured together (26 September, three passes on each of three cards)

| Path | zeros pJ/B | random pJ/B | random / zeros | GB/s | per card, random |
|---|---|---|---|---|---|
| L1 hit, `flw.ps` 32 B (both harts) | **0.39** [0.37–0.41] | **0.54** [0.52–0.56] | 1.37× | 14,488 | a2: 0.55 ± 0.01 · a3: 0.54 ± 0.005 · a1c1: 0.52 ± 0.003 |
| L1 hit, `fsw.ps` 32 B (both harts) | **0.41** [0.38–0.46] | **0.72** [0.66–0.81] | 1.75× | 14,719 | a2: 0.73 ± 0.04 · a3: 0.72 ± 0.002 · a1c1: 0.71 ± 0.01 |
| Tensor load from the shire's own scratchpad | **2.12** [1.85–2.46] | **4.43** [4.06–5.03] | 2.09× | 2,458 | a2: 4.16 ± 0.05 · a3: 4.14 ± 0.02 · a1c1: 4.98 ± 0.03 |
| Tensor store into the shire's own scratchpad | **4.65** [4.25–5.25] | **8.58** [7.84–9.99] | 1.85× | 1,230 | a2: 8.03 ± 0.12 · a3: 7.87 ± 0.02 · a1c1: 9.84 ± 0.10 |
| Tensor load from DRAM | **94.6** [86.2–105.7] | **132.6** [117.9–145.4] | 1.40× | 76 | a2: 134.8 ± 1.8 · a3: 127.3 ± 0.6 · a1c1: 135.8 ± 9.0 |
| Tensor store to DRAM | **94.4** [83.2–110.9] | **141.9** [131.2–157.0] | 1.50× | 76 | a2: 136.4 ± 2.6 · a3: 132.4 ± 0.6 · a1c1: 156.9 ± 0.1 |
| `fsw.ps` stores to DRAM through the L1 (the write-back path) | **247.4** [202.4–288.9] | **341.5** [317.4–373.3] | 1.38× | 27 | a2: 329.7 ± 7.2 · a3: 325.8 ± 3.6 · a1c1: 368.9 ± 2.3 |

## 4.2 Reads by level (memhier, 26 September: the version-3 check's V3-RL, at 600 MHz)

**L1**: both harts of every minion re-reading a private 256 B buffer with 32 B vector loads, in memhier's own loop over a buffer whose contents it does not set. That loop (8 loads per loop iteration) issued a load every 3.2 minion-cycles where the catalogue's (64) issued one every 1.4 (14.5 TB/s), and it reads 40%, 40% and 38% above the L1 row of 4.1 on aifoundry2, aifoundry3 and aifoundry1 card 1 (0.55, 0.54 and 0.52 pJ/B on random data), which is the figure to use. **L2, L3, DRAM and the scratchpads**: hart 0 of every minion streaming 1 KB tensor loads — which skip the L1 but are cached in the L2 and L3 — over a working set sized to each level. The probe does not set the contents of the L2, L3 and DRAM buffers, so those rows are not directly comparable to the zeros and random columns of 4.1 (the DRAM level is within noise of the random-data row), and the L2 and L3 levels move a lot from pass to pass (1.42–4.99 and 7.1–20.5 pJ/B). **The version-3 passes set the scratchpads' contents**, filling them with zeros (odd passes) or random data (even passes) before they are read, and the own scratchpad follows the fill: inside the check's registered bands (1.7–2.3 and 3.7–4.7 pJ/B) on aifoundry2 and aifoundry3, above them on aifoundry1 card 1 (2.55 and 5.03). On the L1 and the own scratchpad no pair of cards differs beyond the 99% interval of their passes. Six passes on each of three cards at 600 MHz, every sample, pinned there on aifoundry3 and held there on the others by a warm die (n = 18); they replace three passes on each of two cards of 23 September, whose scratchpads were not filled. The first measurement of 18 September, one run on aifoundry2, ran with the governor free (its clock averaged 0.62–0.74 GHz across the levels) and is superseded.

| Level | Working set | pJ/B | per card |
|---|---|---|---|
| L1 hits | 256 B per hart, 2,048 harts | **0.75** [0.62–0.88] | a2: 0.77 ± 0.04 · a3: 0.75 ± 0.04 · a1c1: 0.72 ± 0.03 |
| L2 | 256 KB per shire (L2 is 512 KB) | **3.11** [1.42–4.99] | a2: 2.64 ± 0.43 · a3: 2.83 ± 0.44 · a1c1: 3.86 ± 0.38 |
| L3 | 768 KB per shire, 24 MB in all (L3 is 32 MB) | **14.7** [7.1–20.5] | a2: 12.3 ± 2.1 · a3: 13.5 ± 2.2 · a1c1: 18.4 ± 1.9 |
| DRAM | 256 MB in all | **114.6** [89.0–141.3] | a2: 111.5 ± 4.0 · a3: 105.6 ± 5.6 · a1c1: 126.6 ± 5.1 |
| own scratchpad, zeros | 2 MB of the shire's own L2 scratchpad, filled with zeros | **2.25** [2.06–2.61] | a2: 2.11 ± 0.03 · a3: 2.10 ± 0.03 · a1c1: 2.55 ± 0.03 |
| own scratchpad, random data | 2 MB of the shire's own L2 scratchpad, filled with random data | **4.40** [3.94–5.08] | a2: 4.13 ± 0.004 · a3: 4.04 ± 0.05 · a1c1: 5.03 ± 0.03 |
| remote scratchpad, zeros | 2 MB of the scratchpad 16 shire IDs away (2.1 mesh hops on average), filled with zeros | **5.10** [4.40–6.45] | a2: 5.04 ± 0.27 · a3: 4.55 ± 0.07 · a1c1: 5.71 ± 0.40 |
| remote scratchpad, random data | 2 MB of the scratchpad 16 shire IDs away (2.1 mesh hops on average), filled with random data | **11.8** [9.5–14.4] | a2: 11.1 ± 0.8 · a3: 10.8 ± 0.4 · a1c1: 13.6 ± 0.4 |

Passes: 18. Source: `docs/reports/data/2026-09-25-claims-v3/raw/<card>/rl/p<K>/B/` (reduced by `tools/ettelem/analyze_reruns.py --v3-rl` into `docs/reports/data/2026-09-23-energy-manual/reruns.json`).

**What the tables say.**
- **DRAM is 30× the energy of the shire's own scratchpad per byte read**, and 17× per byte written.
- **A DRAM write costs about what a DRAM read costs** (142 vs 133 pJ/B on random data; 1% more on aifoundry2, 4% more on aifoundry3 and 16% more on aifoundry1 card 1; the version-3 check, a separate run of these rows, did not resolve the difference from zero on aifoundry2, aifoundry3 and aifoundry1 card 1: aifoundry2 +8.4 pJ/B [−47.4, +64.1]; aifoundry3 +7.3 pJ/B [−1.9, +16.6]; and aifoundry1 card 1 +14.5 pJ/B [−2.8, +31.8], 99% intervals) — by tensor store, which skips the L1 and the L2. **Through the L1 write-back path the same bytes cost 2.4× more** and arrive at a third of the bandwidth, consistent with each store allocating its line, so that the line is read from DRAM before it is written back and the byte pays for a read and a write. Off-rail it costs 163 pJ against a tensor store's 78 ([Limits of observability, §4.2](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#the-unmetered-remainder-attributed)), and a tensor load plus a tensor store come to 275 of its 341 pJ/B.
- **Even DRAM is data-dependent**: zeros 95, random 133 pJ/B, bars [86–106] and [118–145] well apart. The scratchpad doubles from zeros to random.
- **A scratchpad write is twice a scratchpad read** (4.65 vs 2.12 pJ/B on zeros).
- **An L1 hit is nearly free**: 0.54 pJ/B [0.52–0.56] including the instruction.

Where the bytes' energy goes below the line — the wires, the cache lines, the DRAM rows, the SRAM's own leakage and the rails — is in [4.3](04a-fine-grain.md).

Sources: `docs/reports/data/2026-09-25-claims-v3/raw/<card>/catfull/` (the version-3 full catalogue, reduced by `tools/claims-v3/catfull/reduce.py` into `docs/reports/data/2026-09-23-energy-manual/catalogue.json`), `docs/reports/data/2026-09-18-memhier-aifoundry2/energy/results.json` (18 September).


## 4.4 Irregular access: gathers and scatters by level (E48, 26 September, three passes on each of three cards)

The vector unit's indexed loads and stores move eight 4 B elements per instruction, each from its own address (a byte offset per lane, from a vector register, added to a base). Here both harts of all 1,024 minions issue them back to back, each hart on a table of its own sized to one level, and every figure is per element: elements per second over the chip, and pJ per element above idle, **mean** [lo–hi] over every pass on every card. "Random" is one random word on each of the 64 lines of a 4 KB tile, the tiles visited in a scrambled order: random lines within 4 KB tiles, not uniform addresses over the table. The last column is the same level read contiguously ([4.1](04-bytes-memory.md), 4.2), per 4 B. Operands are random data; zeros are below.

| Level | Table | gather `fgw.ps` | gather past the L1 (`fgwl.ps` to the L2, `fgwg.ps` to the home) | scatter `fscw.ps` | scatter past the L1 (`fscwl.ps`, `fscwg.ps`) | scalar `flw`, same offsets | scalar `fsw`, same offsets | streamed, pJ per 4 B |
|---|---|---|---|---|---|---|---|---|
| L1 | 512 B per hart (the hart's whole L1) | **12.8** [11.9–14.6] pJ, 452 G/s | — | **14.7** [13.9–15.5] pJ, 452 G/s | — | **14.0** [13.4–14.5] pJ, 403 G/s | **25.5** [24.8–26.4] pJ, 402 G/s | 2.14 |
| L2 | 4 KB per hart, 256 KB per shire (half the L2) | **354.5** [329.9–391.6] pJ, 27.4 G/s | `fgwl.ps` **349.6** [327.4–380.7] pJ, 19.6 G/s | **731.5** [676.9–813.9] pJ, 23.5 G/s | `fscwl.ps` **429.4** [405.0–479.2] pJ, 14.5 G/s | **336.0** [315.0–369.4] pJ, 27.5 G/s | **773.6** [710.2–856.1] pJ, 23.6 G/s | 12.4 |
| own scratchpad | 16 KB per hart of the shire's own scratchpad | **367.8** [344.3–399.6] pJ, 27.4 G/s | `fgwl.ps` **361.4** [336.5–392.6] pJ, 19.6 G/s | **690.5** [641.9–762.5] pJ, 23.5 G/s | `fscwl.ps` **402.0** [348.5–447.7] pJ, 14.5 G/s | **351.3** [325.6–387.6] pJ, 27.5 G/s | **729.5** [675.6–815.8] pJ, 23.6 G/s | 17.6 |
| L2 and L3 | 16 KB per hart, 1 MB per shire (32 MB in all) | **1.6** [1.5–1.8] nJ, 8.43 G/s | — | **3.2** [3.0–3.5] nJ, 8.18 G/s | — | — | — | — |
| L3 | 4 KB per hart, read past the L1 and L2 at the line's home slice | — | `fgwg.ps` **1.5** [1.4–1.6] nJ, 6.46 G/s | — | `fscwg.ps` **1.4** [1.3–1.5] nJ, 4.51 G/s | — | — | 58.9 |
| remote scratchpad | 16 KB per hart of a scratchpad 2 mesh hops away | **903.1** [843.1–1010.2] pJ, 10.2 G/s | `fgwg.ps` **965.5** [905.0–1025.6] pJ, 7.43 G/s | **2.0** [1.9–2.2] nJ, 10.2 G/s | `fscwg.ps` **1.1** [1.0–1.2] nJ, 5.18 G/s | — | — | 47.3 |
| L3 and DRAM | 64 KB per hart (128 MB in all) | **9.2** [9.2–9.3] nJ (a3 only), 1.19 G/s | — | — | — | — | — | — |
| DRAM | 256 KB per hart (512 MB in all) | **9.8** [9.2–10.3] nJ, 1.19 G/s | `fgwg.ps` **9.6** [9.1–10.2] nJ, 1.17 G/s | **23.8** [22.2–25.3] nJ, 422 M/s | `fscwg.ps` **19.5** [17.6–21.6] nJ, 498 M/s | **9.2** [8.6–9.9] nJ, 1.19 G/s | — | 530.4 |

Each card's own mean ± its pass-to-pass standard error, pJ per element on random data ("a2", "a3" and "a1c1" as above):

| Level | gather `fgw.ps` | scatter `fscw.ps` |
|---|---|---|
| L1 | a2 13.5 ± 0.59 · a3 12.5 ± 0.31 · a1c1 12.3 ± 0.17 | a2 14.7 ± 0.43 · a3 14.6 ± 0.17 · a1c1 14.8 ± 0.37 |
| L2 | a2 343.2 ± 2.64 · a3 333.1 ± 2.16 · a1c1 387.1 ± 3.15 | a2 701.9 ± 2.50 · a3 679.1 ± 1.23 · a1c1 813.5 ± 0.23 |
| own scratchpad | a2 359.7 ± 3.06 · a3 344.6 ± 0.15 · a1c1 399.3 ± 0.29 | a2 670.6 ± 5.11 · a3 643.8 ± 1.07 · a1c1 757.0 ± 5.24 |
| L2 and L3 | a2 1.60 ± 0.02 · a3 1.51 ± 0.00 · a1c1 1.77 ± 0.02 nJ | a2 3.12 ± 0.02 · a3 2.96 ± 0.00 · a1c1 3.52 ± 0.00 nJ |
| remote scratchpad | a2 888.7 ± 9.62 · a3 847.2 ± 2.68 · a1c1 973.4 ± 18.5 | a2 1.96 ± 0.01 · a3 1.87 ± 0.00 · a1c1 2.13 ± 0.04 nJ |
| L3 and DRAM | a3 9.24 ± 0.04 nJ | — |
| DRAM | a2 9.87 ± 0.18 · a3 9.32 ± 0.08 · a1c1 10.30 ± 0.03 nJ | a2 23.64 ± 0.66 · a3 22.53 ± 0.21 · a1c1 25.14 ± 0.08 nJ |

**What the tables say.**
- **From the L1 a gather costs what a scalar load costs.** 452 G elements/s at 12.8 pJ each, against 403 G/s at 14.0 pJ for scalar `flw` on the same 64 offsets; an instruction's eight elements take 10.89 minion-cycles on every card (the design's model: 8, one element address a cycle; registered 7–12: PASS on every card). The 32 B-block form `fg32w.ps`, one access per instruction with the lanes permuted inside the block, runs 3.9× as fast at 0.30× the energy (1,786 G/s, 3.8 pJ).
- **Past the L1 the line is the unit.** Each element that misses fetches its own 64 B line, and a minion's two miss handlers fetch two at a time: 27.4 G/s from the L2 and 27.4 G/s from the own scratchpad, 1.15× the two-miss-handler bound (23.9 G/s), with one hart or two (the second adds 0.05% or less; PASS on every card), and no faster than eight scalar loads on the same addresses (27.5 G/s). A random word from the L2 costs 354 pJ, 29× the same 4 B streamed; from DRAM 1.19 G/s and 9.8 nJ, 19× streamed: its lines arrive at 76.4 GB/s, DRAM's streaming bandwidth (57–95 GB/s registered: PASS on every card), and 154 pJ per line byte against a tensor load's 133 pJ/B.
- **Skipping the L1 does not help.** `fgwl.ps` reads the L2 at 19.6 G/s, 0.72× the path through the L1, at 350 pJ; and one minion's second hart adds only 3% to it, where the strict per-thread order of L1-bypassing operations predicted 1.6–2.4× (FAIL on every card): the two harts share one limit. The global form `fgwg.ps` reaches the line's home L3 slice at 6.46 G/s for 1.53 nJ.
- **A scatter costs about twice a gather.** Into the L2 731 pJ (2.1× the gather) at 23.5 G/s: each element allocates its line and writes it back. Into DRAM 422 M/s at 23.8 nJ (2.4×). From the L1 14.7 pJ at 452 G/s.
- **Random data costs up to 2.6× zeros**: gathers 1.19× from the L1, 2.12× from the L2 (168 pJ on zeros), 1.84× from the own scratchpad and 1.38× from DRAM (7.1 nJ on zeros); scatters 1.26× into the L1 and 2.56× into the L2.
- **The cards agree.** Every rate is the same on the three cards to 0.02% (10–90% over the configurations); energy per element is 0.965× aifoundry2's on aifoundry3 and 1.085× aifoundry2's on aifoundry1 card 1 in the median over the configurations, each card at its own die temperature. Every tested item was decided card by card on three cards in three machines (aifoundry2, aifoundry3 and aifoundry1 card 1), each with three passes: the L1 issue, the miss-handler bound, the DRAM line rate and exactness held on each; the second hart's share failed on each.
- **Exact on silicon.** All 159 verify launches passed on every card, every gathered element, scattered word and shared counter checked on the host: they are the detector of erratum 1.3 (after a gather or scatter resumed from a trap, the next one can skip elements), and it did not occur. Every timed launch (2,937 per card) also ended with the gather/scatter progress register at 0 on every hart. When every lane scatters to one word, lane 7's value remains, every time on every card.
- **A gap.** The `fgw.ps` gather from 64 KB per hart lost every energy burst on aifoundry2 and aifoundry1 card 1: the pre-registered clock rule drops a burst in which any launch's implied clock (cycles over wall time) falls outside 0.595–0.605 GHz, and one launch in each of its bursts read 0.594 GHz, just under the band, while the telemetry read 600 MHz. The rule was not relaxed: its energy (9.2 nJ) is aifoundry3's alone, as the table marks, and its rate 1.19 G/s is the same as from DRAM.

The per-line and per-element parts of these costs, the patterns, masks, element sizes and lane conflicts are in [4.3](04a-fine-grain.md); scatter-add and the packed atomics are in [6](06-synchronisation.md).

Source: `docs/reports/data/2026-09-25-claims-v3/raw/<card>/gs/p<KS>/` (E48), reduced by `tools/claims-v3/gs/reduce.py` into `docs/reports/data/2026-09-25-claims-v3/results/gs-full.json` (every configuration, per card and pass) and `docs/reports/data/2026-09-25-claims-v3/results/gs.json` (the items); pooled into `manual.json` `gs` by `tools/ettelem/build_energy_manual.py`.
