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
