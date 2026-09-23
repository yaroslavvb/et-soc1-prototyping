# 4.3 Finer grain: wires, lines, rows, and the leakage of the arrays

What a byte costs is not one number. Below, the parts of it that can be separated with the card's own instruments: the distance the byte travels, the line it is part of, the DRAM row it comes from, and the leakage of the memory it sat in. Every figure is a mean over three passes.

## Wires: energy against distance on the mesh

1 KB tensor loads from the scratchpad of a shire exactly *d* hops away on the mesh, every shire reading, at most two readers per target. A straight line through the points gives the energy of the array access and the local path (the intercept) and the energy of one hop of mesh, router and wire per byte (the slope).

| Operands | pJ/B at 0 hops (own scratchpad) | intercept pJ/B | **slope pJ/B per hop** | rms of the fit | points |
|---|---|---|---|---|---|
| zeros | 2.01 | 3.05 | **0.750** | 0.39 | 7 |
| random | 4.29 | 7.90 | **1.812** | 1.09 | 7 |

The slope on random data less the slope on zeros, 1.061 pJ/B per hop, is the switching energy of the wires themselves — what it costs to toggle a byte's worth of mesh links and router flops once. The rest of the slope, 0.750 pJ/B per hop, is what a hop costs whether or not the bits change: clocking, arbitration, buffering. In bits: **132.7 fJ per bit per hop of toggling**.

| hops | zeros pJ/B | random pJ/B | shires reading |
|---|---|---|---|
| 1 | 3.60 | 8.84 | 32 |
| 2 | 4.36 | 11.02 | 32 |
| 3 | 5.00 | 13.13 | 32 |
| 4 | 6.64 | 16.24 | 32 |
| 5 | 7.23 | 18.04 | 32 |
| 6 | 7.79 | 20.01 | 31 |
| 8 | 8.51 | 20.55 | 16 |

## Lines: what opening a 64 B line costs, and the shire cache's banks

32 B vector loads through the L1 from the shire's own scratchpad, striding so that every line is filled once and all, half or a quarter of it is used. Energy per *load* rises as the fill is shared by fewer loads; the difference is the cost of the fill itself.

| Stride | Fills per 32 B load | zeros pJ per load | random pJ per load | zeros pJ/B delivered | random pJ/B delivered |
|---|---|---|---|---|---|
| 32 B | 0.5 | 131.5 | 197.3 | 4.11 | 6.17 |
| 64 B | 1 | 186.7 | 303.0 | 5.83 | 9.47 |
| 128 B | 1 | 178.1 | 305.3 | 5.57 | 9.54 |

Twice the difference between the stride-64 and stride-32 rows is the fill of one 64 B line from the scratchpad into the L1: **110 pJ on zeros, 211 pJ on random data** — 1.7 and 3.3 pJ per byte of line, which agrees with the 2.0 and 4.3 pJ/B a tensor load pays for the same bytes from the same scratchpad. The 101 pJ difference is the toggling of the line's 512 bits, 197 fJ per bit on the path from the shire cache into the L1. What is left in a 32 B load once its share of the fill is taken out — about 76 pJ on zeros — is the L1 hit itself plus the awake core issuing it.

The same scratchpad read with 64 B tensor loads at strides that cycle the shire cache's banks, alternate two of them, or return to the same one (banks are address bits [7:6], sub-banks [9:8]):

| Stride | zeros pJ per 64 B | random pJ per 64 B | GB/s |
|---|---|---|---|
| 64 B | 255.7 | 386.1 | 1126 |
| 128 B | 237.9 | 391.8 | 1121 |
| 256 B | 295.1 | 423.6 | 614 |

## Rows: does the DRAM row pattern matter?

1 KB tensor loads from DRAM by 32 harts (minion 0 of every shire), each over its own 64 MB, so the touched set beats the 32 MB L3 whatever the pattern. Sequential: consecutive kilobytes go to consecutive banks and each bank sees 32 columns of a row before moving on. Row hit: stride 8 KB, so every access is the next column of the same bank and row. Row miss: after every 8 KB a jump to the next row, so every bank sees a new row on every visit. Thirty-two awake minions are 0.06 W, not worth correcting for.

| Pattern | zeros pJ/B | random pJ/B | GB/s |
|---|---|---|---|
| sequential: next bank, 32 columns per row visit | 114.5 ± 3.9 | 147.1 ± 7.9 | 16.9 |
| same bank and row, next column, every access | 118.0 ± 1.0 | 155.7 ± 4.9 | 13.9 |
| new row on every visit to a bank | 114.5 ± 4.5 | 153.4 ± 4.8 | 16.9 |

**The row pattern does not change the energy per byte.** Row hits, row misses and the streaming case agree within their pass-to-pass error on both operand sets. Either the controller closes pages after each access (so every access pays an activation and the baseline already includes it) or the activation is small next to the ~115 pJ/B the transfer costs; the card's instruments cannot tell which, and for a programmer it makes no difference: **on this card a DRAM byte costs the same whatever order the rows are visited in.**

An earlier version of this experiment with all 1,024 minions and 32 KB touched per hart fitted in the L3 and measured that instead: **7.9 pJ/B on zeros, 19.7 on random data at 1072 GB/s** — the L3, read by tensor loads through the mesh, which the 18 September table put at 10.8 pJ/B at a higher clock.

## Placement inside a shire: which neighbourhood reads

The shire's own scratchpad read by only one of its four neighbourhoods at a time (8 minions each), random data.

| Neighbourhood | pJ/B | GB/s |
|---|---|---|
| 0 (minions 0–7) | 3.96 ± 0.13 | 966 |
| 1 (minions 8–15) | 3.84 ± 0.19 | 967 |
| 2 (minions 16–23) | 4.24 ± 0.10 | 967 |
| 3 (minions 24–31) | 4.00 ± 0.17 | 966 |

## Leakage of the arrays: the SRAM rail against temperature

The service processor's SRAM rail during every idle stretch of the session, against die temperature. The rail feeds the 128 MB of on-chip SRAM (16 MB of L2, 32 MB of L3, 80 MB of scratchpad). Fitted with the same shape as the idle law:

$$P_\text{SRAM}(T) = -0.32\,\mathrm{W} + 2.81\,\mathrm{W}\; e^{(T-80\,^\circ\mathrm{C})/36\,^\circ\mathrm{C}}$$

- **21.9 mW per MB of SRAM at 80 °C**, 2.6 nW per bit including the cache logic on the same rail, rising 78 mW per °C for the whole 128 MB. Measured: 1.60 W at 67 °C, 1.92 W at 72 °C, 2.26 W at 77 °C, 2.63 W at 82 °C.
- This is what the memory costs for existing, per second, whatever runs; a byte that sits in scratchpad for a second costs 20929.8 pJ of leakage at 80 °C, against the 4.3 pJ it costs to read it once.

| Die °C | SRAM rail W | samples |
|---|---|---|
| 67 | 1.598 | 4 |
| 68 | 1.655 | 4 |
| 69 | 1.715 | 3 |
| 70 | 1.777 | 3 |
| 71 | 1.858 | 10 |
| 72 | 1.922 | 5 |
| 73 | 1.998 | 14 |
| 74 | 2.076 | 13 |
| 75 | 2.134 | 16 |
| 76 | 2.202 | 22 |
| 77 | 2.258 | 133 |
| 78 | 2.337 | 239 |
| 79 | 2.412 | 464 |
| 80 | 2.483 | 170 |
| 81 | 2.559 | 61 |
| 82 | 2.626 | 13 |

## Where the current flows: each class of operation by rail

The service processor meters three rails — the minions, the on-chip SRAM, and the mesh — and board power covers everything including the regulators' own losses. The split of a burst's power over idle across those rails, read from the last second of each burst (the rail figures lag by about two seconds), averaged over the instructions in each class on random data. What is not on a metered rail is the regulators and whatever else has no sensor.

| Class | W over idle | minions | SRAM | mesh | unmetered |
|---|---|---|---|---|---|
| Scalar integer | 4.12 | 79% | 1% | 0% | 19% |
| Scalar multiply | 2.37 | 72% | 2% | -0% | 26% |
| Scalar float | 13.29 | 82% | 2% | 1% | 15% |
| Vector float | 22.70 | 81% | 1% | 1% | 17% |
| Vector integer | 12.22 | 81% | 2% | 1% | 16% |
| Transcendental | 21.90 | 81% | 1% | 1% | 17% |
| L1 hits | 7.13 | 80% | 1% | 0% | 18% |
| L1-bypass to the L2 | 8.09 | 29% | 63% | 1% | 7% |
| Atomics, local L2 | 5.07 | 27% | 58% | 1% | 14% |
| Atomics, home L3 | 4.37 | 24% | 23% | 32% | 22% |
| Own scratchpad, tensor load | 10.51 | 26% | 67% | 1% | 6% |
| Own scratchpad, tensor store | 10.14 | 20% | 74% | 1% | 6% |
| Scratchpad 1 hop away | 13.19 | 14% | 50% | 27% | 8% |
| Scratchpad 3 hops away | 15.63 | 11% | 36% | 40% | 13% |
| Scratchpad 6 hops away | 16.51 | 8% | 25% | 49% | 19% |
| DRAM, tensor load | 9.84 | 2% | 11% | 17% | 70% |
| DRAM, tensor store | 10.67 | 3% | 15% | 18% | 64% |
| DRAM through the L1 write-back path | 9.22 | 9% | 11% | 20% | 59% |

**The mesh rail alone**, against hop distance on random data: 1.287 pJ/B per hop with an intercept of 1.50 pJ/B (the cost of leaving the shire). This is the wire and router energy measured on its own supply, independently of the board-power fit above.

| hops | mesh rail, pJ/B |
|---|---|
| 1 | 2.41 |
| 2 | 3.79 |
| 3 | 5.22 |
| 4 | 7.25 |
| 5 | 8.45 |
| 6 | 9.75 |
| 8 | 10.95 |

Sources: `docs/reports/data/2026-09-23-catalogue-aifoundry2/` and `-aifoundry3/`, reduced by `workloads/enercat/analyze_catalogue.py` into `docs/reports/data/2026-09-23-energy-manual/catalogue.json`.

