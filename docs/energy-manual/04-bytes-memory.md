# 4. Bytes through the memory hierarchy

Energy per byte moved, above idle, at 600 MHz. Zeros and random data, because the bus toggles are a large part of the cost at every level.

Every entry is **mean** [lo–hi]: the mean over every pass on every card, and the full range those passes spanned. "a2" and "a3" are aifoundry2 and aifoundry3, each as its own mean ± its pass-to-pass standard error.

## 4.1 Reads and writes, measured together (23 September, three passes on each card)

| Path | zeros pJ/B | random pJ/B | random / zeros | GB/s | per card, random |
|---|---|---|---|---|---|
| L1 hit, `flw.ps` 32 B (both harts) | **0.39** [0.37–0.41] | **0.54** [0.51–0.56] | 1.39× | 0 | a2: 0.55 ± 0.01 · a3: 0.52 ± 0.01 |
| L1 hit, `fsw.ps` 32 B (both harts) | **0.43** [0.41–0.45] | **0.74** [0.72–0.76] | 1.72× | 0 | a2: 0.76 ± 0.00 · a3: 0.72 ± 0.00 |
| Tensor load from the shire's own scratchpad | **2.01** [1.97–2.06] | **4.21** [4.01–4.36] | 2.09× | 2458 | a2: 4.29 ± 0.04 · a3: 4.12 ± 0.06 |
| Tensor store into the shire's own scratchpad | **4.58** [4.42–4.75] | **8.10** [7.92–8.34] | 1.77× | 1231 | a2: 8.27 ± 0.04 · a3: 7.92 ± 0.00 |
| Tensor load from DRAM | **90.68** [86.43–94.22] | **129.11** [127.48–131.46] | 1.42× | 76 | a2: 129.96 ± 0.81 · a3: 128.26 ± 0.69 |
| Tensor store to DRAM | **88.80** [81.79–94.88] | **136.19** [130.15–142.37] | 1.53× | 76 | a2: 140.88 ± 1.25 · a3: 131.50 ± 0.77 |
| `fsw.ps` streaming to DRAM through the L1 write-back path | **237.56** [231.79–252.74] | **332.65** [315.36–352.85] | 1.40× | 27 | a2: 343.88 ± 8.11 · a3: 321.43 ± 3.16 |

## 4.2 Reads by level (memhier, re-run at a pinned 600 MHz on 23 September)

Plain vector loads streaming over a working set sized to each level, both harts of every minion. The first measurement of 18 September ran with the governor free (the clock sat at 0.67–0.77 GHz on the larger sets) and is superseded; these passes were at 600 MHz in every sample.

| Level | Working set | pJ/B | per card |
|---|---|---|---|
| L1 hits | 256 B per hart, 2,048 harts | **0.77** [0.66–0.88] | a2: 0.86 ± 0.01 · a3: 0.68 ± 0.01 |
| L2 | 256 KB per shire (L2 is 512 KB) | **2.51** [2.36–2.64] | a2: 2.61 ± 0.02 · a3: 2.40 ± 0.02 |
| L3 | 768 KB per shire, 24 MB in all (L3 is 32 MB) | **10.51** [9.61–11.44] | a2: 10.69 ± 0.26 · a3: 10.32 ± 0.57 |
| DRAM | 256 MB in all | **121.96** [116.78–129.03] | a2: 122.90 ± 3.54 · a3: 121.02 ± 2.07 |
| own scratchpad | 2 MB of the shire's own L2 scratchpad | **2.52** [2.39–2.64] | a2: 2.40 ± 0.00 · a3: 2.63 ± 0.01 |
| remote scratchpad | 2 MB of the scratchpad 16 shires away | **6.65** [5.31–7.48] | a2: 6.17 ± 0.43 · a3: 7.14 ± 0.27 |

Passes: 6. Source: `docs/reports/data/2026-09-23-reruns-aifoundry2-warm/`, `-aifoundry3/`.

**What the tables say.**
- **DRAM is 31× the energy of the shire's own scratchpad per byte read**, and 17× per byte written.
- **A DRAM write costs about what a DRAM read costs** (136 vs 129 pJ/B on random data) — by tensor store, which bypasses the caches. **Through the L1 write-back path the same bytes cost 2.4× more** and arrive at a third of the bandwidth: every store allocates a line, and the line goes down through L2 and L3.
- **Even DRAM is data-dependent**: zeros 91, random 129 pJ/B, bars [86–94] and [127–131] well apart. The scratchpad doubles from zeros to random.
- **A scratchpad write is twice a scratchpad read** (4.58 vs 2.01 pJ/B on zeros).
- **An L1 hit is nearly free**: 0.54 pJ/B [0.51–0.56] including the instruction.

Where the bytes' energy goes below the line — the wires, the cache lines, the DRAM rows, the SRAM's own leakage and the rails — is in 4a.

Sources: `docs/reports/data/2026-09-23-catalogue-aifoundry2/`, `-aifoundry3/`, `docs/reports/data/2026-09-18-memhier-aifoundry2/energy/results.json`.
