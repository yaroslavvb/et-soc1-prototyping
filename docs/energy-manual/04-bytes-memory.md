# 4. Bytes through the memory hierarchy

Energy per byte moved, above idle, at 600 MHz. Zeros and random data, because the bus toggles are a large part of the cost at every level.

## 4.1 Reads and writes, measured together (23 September)

| Path | zeros pJ/B | random pJ/B | random / zeros | GB/s | aifoundry3, random |
|---|---|---|---|---|---|
| L1 hit, `flw.ps` 32 B (both harts) | 0.36 | **0.54** | 1.48× | 14648 | 0.50 |
| L1 hit, `fsw.ps` 32 B (both harts) | 0.47 | **0.78** | 1.66× | 14395 | 0.74 |
| Tensor load from the shire's own scratchpad | 2.02 | **4.23** | 2.10× | 2458 | 4.08 |
| Tensor store into the shire's own scratchpad | 4.38 | **8.04** | 1.84× | 1230 | 7.82 |
| Tensor load from DRAM | 94.01 | **133.93** | 1.42× | 76 | 128.56 |
| Tensor store to DRAM | 86.82 | **139.82** | 1.61× | 76 | 132.24 |
| `fsw.ps` streaming to DRAM through the L1 write-back path | 246.57 | **345.29** | 1.40× | 27 | 325.12 |

## 4.2 Reads by level (18 September, memhier)

| Level | Working set | pJ/B | GB/s | Clock during the run |
|---|---|---|---|---|
| l1 | L1 hits: 256 B per hart, 2048 harts | 1.66 | 7564 | 0.74 GHz implied |
| l2 | 256 KB per shire (L2 is 512 KB) | 4.05 | 2744 | 0.68 GHz implied |
| l3 | 768 KB per shire > L2, 24 MB in total < 32 MB of L3 | 10.85 | 1010 | 0.62 GHz implied |
| dram | 256 MB in total | 133.31 | 76 | 0.67 GHz implied |
| scp-local | 2 MB of the shire's own L2 scratchpad | 2.55 | 2523 | 0.62 GHz implied |
| scp-remote | 2 MB of the scratchpad 16 shires away | 6.25 | 981 | 0.64 GHz implied |

*Caveat:* measured on 2026-09-18 with the governor free to move the clock; implied_ghz says where it sat. The two levels re-measured at a pinned 600 MHz on 23 September (4.1) agree with these to within the data dependence: DRAM 133.31 here against 133.93 on random data now.

**What the tables say.**
- **DRAM is 32× the energy of the shire's own scratchpad per byte read**, and 17× per byte written.
- **A DRAM write costs about what a DRAM read costs** (140 vs 134 pJ/B on random data) — by tensor store, which bypasses the caches. **Through the L1 write-back path the same bytes cost 2.5× more** and arrive at a third of the bandwidth: every store allocates a line, and the line goes down through L2 and L3.
- **Even DRAM is data-dependent**: zeros 94, random 134 pJ/B. The scratchpad doubles from zeros to random.
- **A scratchpad write is twice a scratchpad read** (4.38 vs 2.02 pJ/B on zeros).
- **An L1 hit is nearly free**: 0.54 pJ/B including the instruction, 0.31 pJ/B over the awake core.

Sources: `docs/reports/data/2026-09-23-enercat-aifoundry2/`, `docs/reports/data/2026-09-18-memhier-aifoundry2/energy/results.json`.
