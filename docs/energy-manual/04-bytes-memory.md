# 4. Bytes through the memory hierarchy

Energy per byte moved, above idle, at 600 MHz. Zeros and random data, because the data is a large part of the cost at every level: random data costs 1.4–2.1× what zeros cost on the paths of 4.1.

Every entry is **mean** [lo–hi]: the mean over every pass on every card, and the full range those passes spanned. "a2" and "a3" are aifoundry2 and aifoundry3, each as its own mean ± its pass-to-pass standard error.

## 4.1 Reads and writes, measured together (23 September, three passes on each card)

| Path | zeros pJ/B | random pJ/B | random / zeros | GB/s | per card, random |
|---|---|---|---|---|---|
| L1 hit, `flw.ps` 32 B (both harts) | **0.39** [0.37–0.41] | **0.54** [0.51–0.56] | 1.39× | 14,184 | a2: 0.55 ± 0.01 · a3: 0.52 ± 0.01 |
| L1 hit, `fsw.ps` 32 B (both harts) | **0.43** [0.41–0.45] | **0.74** [0.72–0.76] | 1.72× | 14,203 | a2: 0.76 ± 0.003 · a3: 0.72 ± 0.001 |
| Tensor load from the shire's own scratchpad | **2.01** [1.97–2.06] | **4.21** [4.01–4.36] | 2.09× | 2,458 | a2: 4.29 ± 0.04 · a3: 4.12 ± 0.06 |
| Tensor store into the shire's own scratchpad | **4.58** [4.42–4.75] | **8.10** [7.92–8.34] | 1.77× | 1,231 | a2: 8.27 ± 0.04 · a3: 7.92 ± 0.003 |
| Tensor load from DRAM | **90.7** [86.4–94.2] | **129.1** [127.5–131.5] | 1.42× | 76 | a2: 130.0 ± 0.8 · a3: 128.3 ± 0.7 |
| Tensor store to DRAM | **88.8** [81.8–94.9] | **136.2** [130.2–142.4] | 1.53× | 76 | a2: 140.9 ± 1.2 · a3: 131.5 ± 0.8 |
| `fsw.ps` stores to DRAM through the L1 (the write-back path) | **237.6** [231.8–252.7] | **332.7** [315.4–352.9] | 1.40× | 27 | a2: 343.9 ± 8.1 · a3: 321.4 ± 3.2 |

## 4.2 Reads by level (memhier, re-run at 600 MHz on 23 September)

**L1**: both harts of every minion re-reading a private 256 B buffer with 32 B vector loads, in memhier's own loop over a buffer whose contents it does not set. That loop (8 loads per loop iteration) issued a load every 3.2 minion-cycles where the catalogue's (64) issued one every 1.4 (14.2 TB/s), and it reads 56% above the L1 row of 4.1 on aifoundry2 and 31% on aifoundry3 (0.55 and 0.52 pJ/B on random data), which is the figure to use. **L2, L3, DRAM and the scratchpads**: hart 0 of every minion streaming 1 KB tensor loads — which skip the L1 but are cached in the L2 and L3 — over a working set sized to each level. The probe does not set the memory's contents, so these rows are not directly comparable to the zeros and random columns of 4.1: the own scratchpad sits between them, and the DRAM level is within noise of the random-data row. **On L1, L2 and the own scratchpad the two cards differ** beyond their pass-to-pass error (aifoundry3 is lower on L1 and L2, higher on its own scratchpad), and on L1 and the own scratchpad not by the 0.95 of section 8, so for those rows use the per-card column; contents left in the unset buffers, which can differ by card, are as likely a cause as the card. Three passes on each card at 600 MHz, pinned there on aifoundry3 and held there on aifoundry2 by a warm die (n = 6). The first measurement of 18 September, one run on aifoundry2, ran with the governor free (its clock averaged 0.62–0.74 GHz across the levels) and is superseded.

| Level | Working set | pJ/B | per card |
|---|---|---|---|
| L1 hits | 256 B per hart, 2,048 harts | **0.77** [0.66–0.88] | a2: 0.86 ± 0.01 · a3: 0.68 ± 0.01 |
| L2 | 256 KB per shire (L2 is 512 KB) | **2.51** [2.36–2.64] | a2: 2.61 ± 0.02 · a3: 2.40 ± 0.02 |
| L3 | 768 KB per shire, 24 MB in all (L3 is 32 MB) | **10.5** [9.6–11.4] | a2: 10.7 ± 0.3 · a3: 10.3 ± 0.6 |
| DRAM | 256 MB in all | **122.0** [116.8–129.0] | a2: 122.9 ± 3.5 · a3: 121.0 ± 2.1 |
| own scratchpad | 2 MB of the shire's own L2 scratchpad | **2.52** [2.39–2.64] | a2: 2.40 ± 0.003 · a3: 2.63 ± 0.01 |
| remote scratchpad | 2 MB of the scratchpad 16 shire IDs away (2.1 mesh hops on average) | **6.65** [5.31–7.48] | a2: 6.17 ± 0.43 · a3: 7.14 ± 0.27 |

Passes: 6. Source: `docs/reports/data/2026-09-23-reruns-aifoundry2-warm/`, `-aifoundry3/`.

**What the tables say.**
- **DRAM is 31× the energy of the shire's own scratchpad per byte read**, and 17× per byte written.
- **A DRAM write costs about what a DRAM read costs, within 15%** (136 vs 129 pJ/B on random data; 8.4% more on aifoundry2, 2.5% on aifoundry3) — by tensor store, which skips the L1 and the L2. **Through the L1 write-back path the same bytes cost 2.4× more** and arrive at a third of the bandwidth, consistent with each store allocating its line, so that the line is read from DRAM before it is written back and the byte pays for a read and a write. Off-rail it costs 174 pJ against a tensor store's 81 ([Limits of observability, §4.2](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#the-unmetered-remainder-attributed)), and a tensor load plus a tensor store come to 265 of its 333 pJ/B.
- **Even DRAM is data-dependent**: zeros 91, random 129 pJ/B, bars [86–94] and [127–131] well apart. The scratchpad doubles from zeros to random.
- **A scratchpad write is twice a scratchpad read** (4.58 vs 2.01 pJ/B on zeros).
- **An L1 hit is nearly free**: 0.54 pJ/B [0.51–0.56] including the instruction.

Where the bytes' energy goes below the line — the wires, the cache lines, the DRAM rows, the SRAM's own leakage and the rails — is in [4.3](04a-fine-grain.md).

Sources: `docs/reports/data/2026-09-23-catalogue-aifoundry2/`, `-aifoundry3/`, `docs/reports/data/2026-09-18-memhier-aifoundry2/energy/results.json`.
