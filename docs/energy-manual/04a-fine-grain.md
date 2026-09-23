# 4.3 Finer grain: wires, lines, rows, and the leakage of the arrays

What a byte costs is not one number. Below, the parts of it that can be separated with the card's own instruments: the distance the byte travels, the line it is part of, the DRAM row it comes from, and the leakage of the memory it sat in. **Every figure is the mean over three passes on each of two cards, and a bracket is the range those six measurements spanned.** Fits are made per card and both are shown.

## Wires: energy against distance on the mesh

1 KB tensor loads from the scratchpad of a shire exactly *d* hops away on the mesh, every shire reading, at most two readers per target. A straight line through the points gives the energy of the array access and the local path (the intercept) and the energy of one hop of mesh, router and wire per byte (the slope).

| Operands | Card | own scratchpad pJ/B | intercept pJ/B | **slope pJ/B per hop** | rms of the fit |
|---|---|---|---|---|---|
| zeros | aifoundry2 | 2.01 | 3.05 | **0.750** | 0.39 |
| zeros | aifoundry3 | 2.01 | 3.08 | **0.643** | 0.47 |
| random | aifoundry2 | 4.29 | 7.90 | **1.812** | 1.09 |
| random | aifoundry3 | 4.12 | 7.52 | **1.675** | 0.99 |

**One hop costs 0.70 pJ/B on zeros [0.64–0.75 across the cards] and 1.74 pJ/B on random data [1.67–1.81].** The difference between the two, 1.05 pJ/B per hop [1.03–1.06], is the switching energy of the wires themselves — **131 fJ per bit per hop of toggling** [129–133]. The rest, what a hop costs whether or not the bits change, is clocking, arbitration and buffering.

| hops | zeros pJ/B [range over both cards, 6 runs] | random pJ/B [range] | shires reading |
|---|---|---|---|
| 1 | **3.47** [3.11–3.67] | **8.65** [8.41–8.94] | 32 |
| 2 | **4.26** [4.08–4.45] | **10.73** [10.38–11.03] | 32 |
| 3 | **4.98** [4.64–5.19] | **12.63** [11.77–13.18] | 32 |
| 4 | **6.40** [5.96–6.86] | **15.78** [15.30–16.31] | 32 |
| 5 | **6.90** [6.37–7.36] | **17.56** [16.99–18.27] | 32 |
| 6 | **7.68** [7.44–7.86] | **19.22** [17.99–20.16] | 31 |
| 8 | **7.97** [7.23–8.53] | **19.93** [19.16–20.89] | 16 |

## Lines: what opening a 64 B line costs, and the shire cache's banks

32 B vector loads through the L1 from the shire's own scratchpad, striding so that every line is filled once and all, half or a quarter of it is used. Energy per *load* rises as the fill is shared by fewer loads; the difference is the cost of the fill itself.

| Stride | Fills per 32 B load | zeros pJ per load (card 2) | random pJ per load (card 2) | zeros pJ/B delivered [range, both cards] | random pJ/B delivered [range] |
|---|---|---|---|---|---|
| 32 B | 0.5 | 131.5 | 197.3 | **4.08** [3.93–4.31] | **6.03** [5.67–6.33] |
| 64 B | 1 | 186.7 | 303.0 | **5.66** [5.37–5.95] | **9.24** [8.96–9.68] |
| 128 B | 1 | 178.1 | 305.3 | **5.60** [5.28–5.75] | **9.24** [8.89–9.71] |

Twice the difference between the stride-64 and stride-32 rows is the fill of one 64 B line from the scratchpad into the L1: **110 pJ on zeros, 211 pJ on random data** — 1.7 and 3.3 pJ per byte of line, which agrees with the 2.0 and 4.3 pJ/B a tensor load pays for the same bytes from the same scratchpad. The 101 pJ difference is the toggling of the line's 512 bits, 197 fJ per bit on the path from the shire cache into the L1. What is left in a 32 B load once its share of the fill is taken out — about 76 pJ on zeros — is the L1 hit itself plus the awake core issuing it.

The same scratchpad read with 64 B tensor loads at strides that cycle the shire cache's banks, alternate two of them, or return to the same one (banks are address bits [7:6], sub-banks [9:8]):

| Stride | zeros pJ per 64 B [range] | random pJ per 64 B [range] | GB/s |
|---|---|---|---|
| 64 B | 248.3 [231.7–258.2] | 382.1 [373.1–391.9] | 1126 |
| 128 B | 235.5 [220.4–261.5] | 380.6 [367.2–400.0] | 1121 |
| 256 B | 276.8 [243.0–307.4] | 422.3 [397.7–461.8] | 614 |

## Rows: does the DRAM row pattern matter?

1 KB tensor loads from DRAM by 32 harts (minion 0 of every shire), each over its own 64 MB, so the touched set beats the 32 MB L3 whatever the pattern. Sequential: consecutive kilobytes go to consecutive banks and each bank sees 32 columns of a row before moving on. Row hit: stride 8 KB, so every access is the next column of the same bank and row. Row miss: after every 8 KB a jump to the next row, so every bank sees a new row on every visit. Thirty-two awake minions are 0.06 W, not worth correcting for.

| Pattern | zeros pJ/B [range over 3 passes, one card] | random pJ/B [range] | GB/s |
|---|---|---|---|
| sequential: next bank, 32 columns per row visit | **114.5** [106.8–118.4] | **147.1** [136.3–162.4] | 16.9 |
| same bank and row, next column, every access | **118.0** [116.6–119.8] | **155.7** [145.9–160.8] | 13.9 |
| new row on every visit to a bank | **114.5** [105.6–119.1] | **153.4** [147.1–162.9] | 16.9 |

**The row pattern does not change the energy per byte.** Row hits, row misses and the streaming case agree within their pass-to-pass error on both operand sets. Either the controller closes pages after each access (so every access pays an activation and the baseline already includes it) or the activation is small next to the ~115 pJ/B the transfer costs; the card's instruments cannot tell which, and for a programmer it makes no difference: **on this card a DRAM byte costs the same whatever order the rows are visited in.**

An earlier version of this experiment with all 1,024 minions and 32 KB touched per hart fitted in the L3 and measured that instead: **7.9 pJ/B on zeros, 19.7 on random data at 1072 GB/s** — the L3, read by tensor loads through the mesh, which the 18 September table put at 10.8 pJ/B at a higher clock.

## Placement inside a shire: which neighbourhood reads

The shire's own scratchpad read by only one of its four neighbourhoods at a time (8 minions each), random data.

| Neighbourhood | pJ/B [range, both cards] | GB/s |
|---|---|---|
| 0 (minions 0–7) | **3.95** [3.79–4.20] | 966 |
| 1 (minions 8–15) | **3.83** [3.49–4.14] | 967 |
| 2 (minions 16–23) | **4.14** [3.87–4.43] | 967 |
| 3 (minions 24–31) | **3.99** [3.81–4.35] | 966 |

## Leakage of the arrays: the SRAM rail against temperature

The service processor's SRAM rail during every idle stretch of the session, against die temperature. The rail feeds the 128 MB of on-chip SRAM (16 MB of L2, 32 MB of L3, 80 MB of scratchpad). Fitted with the same shape as the idle law:

$$P_\text{SRAM}(T) = -0.32\,\mathrm{W} + 2.81\,\mathrm{W}\; e^{(T-80\,^\circ\mathrm{C})/36\,^\circ\mathrm{C}}$$

- **21.9 mW per MB of SRAM at 80 °C**, 2.6 nW per bit including the cache logic on the same rail, rising 78 mW per °C for the whole 128 MB. Measured: 1.60 W at 67 °C, 1.92 W at 72 °C, 2.26 W at 77 °C, 2.63 W at 82 °C.
- This is what the memory costs for existing, per second, whatever runs; a byte that sits in scratchpad for a second costs 20929.8 pJ of leakage at 80 °C, against the 4.3 pJ it costs to read it once.
- The same rail on aifoundry3, which idles 20 °C cooler: 1.90 W at 51 °C, 1.98 W at 52 °C, 2.01 W at 53 °C, 2.06 W at 54 °C, 2.10 W at 55 °C; fitted with the same shape it gives 27.4 mW/MB at 80 °C, so across the two cards the figure is **25 mW/MB [22–27] at 80 °C**, with the caveat that each card's range of temperatures is narrow and the second's is an extrapolation.

| Die °C | SRAM rail W, aifoundry2 | idle stretches | SRAM rail W, aifoundry3 | idle stretches |
|---|---|---|---|---|
| 51 | — | — | 1.900 | 9 |
| 52 | — | — | 1.980 | 14 |
| 53 | — | — | 2.007 | 154 |
| 54 | — | — | 2.061 | 803 |
| 55 | — | — | 2.102 | 175 |
| 67 | 1.598 | 4 | — | — |
| 68 | 1.655 | 4 | — | — |
| 69 | 1.715 | 3 | — | — |
| 70 | 1.777 | 3 | — | — |
| 71 | 1.858 | 10 | — | — |
| 72 | 1.922 | 5 | — | — |
| 73 | 1.998 | 14 | — | — |
| 74 | 2.076 | 13 | — | — |
| 75 | 2.134 | 16 | — | — |
| 76 | 2.202 | 22 | — | — |
| 77 | 2.258 | 133 | — | — |
| 78 | 2.337 | 239 | — | — |
| 79 | 2.412 | 464 | — | — |
| 80 | 2.483 | 170 | — | — |
| 81 | 2.559 | 61 | — | — |
| 82 | 2.626 | 13 | — | — |

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

## What is on no metered rail: attributed, and a droop meter for DRAM

The remainder — board power minus the three rails — cannot be metered with anything on the card, but over the whole catalogue it can be attributed: each burst's unmetered watts fitted as a fraction of each rail's watts plus a cost per DRAM byte, no intercept.

| unmetered W of a burst = | aifoundry2 | aifoundry3 |
|---|---|---|
| × minion-rail W | 0.196 ± 0.003 | 0.177 ± 0.002 |
| × SRAM-rail W | 0.050 ± 0.017 | 0.064 ± 0.014 |
| × mesh-rail W | 0.286 ± 0.021 | 0.264 ± 0.019 |
| per DRAM byte | 72.9 ± 1.6 pJ/B | 68.1 ± 1.4 pJ/B |
| residual rms, bursts | 0.35 W, n = 392 | 0.30 W, n = 386 |

- **An instruction's unmetered energy is the regulator's**: 20% of what the minion rail delivers is lost between the 12 V input and the core, and nothing else moves. The 18% "unmetered" share of the arithmetic classes above is this.
- **A DRAM byte's unmetered energy is the memory's**: 73 pJ per byte in the DDR PHY, the I/O rail and the DRAM chips, on top of the 50–60 pJ the mesh, the SRAM and the delivery losses take on the way. A byte written through the L1 costs twice that off-rail, because the line is read from DRAM before it is written.
- **The mesh coefficient is not all regulator**: 29% is too much for a delivery loss; the memory shires' own logic, on an unmetered rail, works whenever the mesh moves bytes to them.
- What the fit cannot say: how the idle 12–15 W splits between DDR, PCIe, the IO shire, Maxion and the regulators' own draw, or how the DRAM term splits below its regulator. That is the subject of the observability report's improvement ladder.

**A droop meter for DRAM.** The memory shires' Moortec voltage monitors report the 0.8 V DDR rail every 133 ms (`die_mv.ddr` in every telemetry file; 767 mV at idle against an 800 mV set point). Across the 386 bursts it droops **0.84 mV per watt of off-rail DRAM power** (plus 0.025 mV per watt of anything else; rms 0.36 mV): 1 mV ≈ 1.2 W of DRAM at 10 Hz, from a sensor that was always there. It is calibrated against the fit above, so it is not independent of the board meter, but it responds to DRAM traffic alone and does not drift with the die temperature. The minion rail sags 0.068 mV per watt the cores draw, the IR drop the spatial temperature brief mapped shire by shire.

| Burst (aifoundry2) | W over idle | DRAM W off-rail | DDR-rail droop, mV | minion-rail droop, mV |
|---|---|---|---|---|
| `add/zeros/h2` | 2.68 | — | 0.00 | -0.02 |
| `fmadd.ps/random/h2` | 26.05 | — | 0.53 | 1.65 |
| `st_stream/dram/random` | 9.22 | 4.68 | 4.27 | -0.02 |
| `tload/dram/random` | 9.84 | 6.29 | 5.64 | 0.00 |
| `tload/dram/zeros` | 7.09 | 4.83 | 3.93 | 0.00 |
| `tload/scp/random` | 10.51 | — | 1.74 | 0.00 |
| `tstore/dram/random` | 10.67 | 6.16 | 5.95 | -0.02 |
| `wire/hop6/random` | 16.51 | — | 1.05 | 0.00 |


Sources: `docs/reports/data/2026-09-23-catalogue-aifoundry2/` and `-aifoundry3/`, reduced by `workloads/enercat/analyze_catalogue.py` into `docs/reports/data/2026-09-23-energy-manual/catalogue.json`; the attribution and the droop in `unmetered_fit.json` beside it.

