# 4.3 Finer grain: wires, lines, rows, and the leakage of the arrays

What a byte costs is not one number. Below, the parts of it that can be separated with the card's own instruments: the distance the byte travels, the line it is part of, the DRAM row it comes from, and the leakage of the memory it sat in. **Every figure is the mean over three passes on each of three cards (26 September), and a bracket is the range those nine measurements spanned.** Fits are made per card and all are shown.

## Wires: energy against distance on the mesh

1 KB tensor loads from the scratchpad of a shire exactly *d* hops away on the mesh, all 32 shires reading up to 5 hops (31 at 6 hops and 16 at 8, so the 8-hop point has half the traffic), at most two readers per target. A straight line through the points gives the energy of the array access and the local path (the intercept) and the energy of one hop of mesh, router and wire per byte (the slope), fitted over 1–8 hops.

| Operands | Card | own scratchpad pJ/B | intercept pJ/B | **slope pJ/B per hop** | rms of the fit |
|---|---|---|---|---|---|
| zeros | aifoundry2 | 1.98 | 3.29 | **0.660** | 0.49 |
| zeros | aifoundry3 | 1.97 | 3.27 | **0.620** | 0.49 |
| zeros | aifoundry1 card 1 | 2.41 | 3.86 | **0.727** | 0.58 |
| random | aifoundry2 | 4.16 | 7.81 | **1.779** | 1.08 |
| random | aifoundry3 | 4.14 | 7.51 | **1.722** | 1.08 |
| random | aifoundry1 card 1 | 4.98 | 9.35 | **1.910** | 1.18 |

**Fitted over 1–8 hops, one hop costs 0.67 pJ/B on zeros [0.62–0.73 across the cards] and 1.80 pJ/B on random data [1.72–1.91].** The difference between the two, 1.13 pJ/B per hop [1.10–1.18], is what random data adds over zeros, the data-dependent energy of the links and routers — **142 fJ per random bit per hop** [138–148]: part of it is bits that differ from one flit (the unit the mesh moves as a whole) to the next and part is the ones carried, which cost even when they do not change; [Heat per millimetre](https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm) separates the two with chosen bit patterns and converts them to fJ per bit·mm. The rest, what a hop costs on all-zero data, is clocking, arbitration and buffering.

**Over 1–6 hops**, leaving out d = 8, where only 16 shires have a partner and the point sits nearly level with d = 6, the same data give 2.23, 2.19 and 2.40 pJ/B per hop on random data (aifoundry2, aifoundry3 and aifoundry1 card 1) and 170, 170 and 179 fJ per random bit per hop, which is what [Heat per millimetre](https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm) measures (2.17 pJ/B per hop on board power, loaded mesh): use its figures for wires.

| hops | zeros pJ/B [range over three cards, 9 runs] | random pJ/B [range] | shires reading |
|---|---|---|---|
| 1 | **3.85** [3.45–4.28] | **9.10** [7.82–10.47] | 32 |
| 2 | **4.48** [4.11–5.02] | **11.35** [10.44–12.80] | 32 |
| 3 | **5.35** [4.85–5.95] | **13.43** [12.44–15.07] | 32 |
| 4 | **6.58** [6.06–7.50] | **16.47** [15.46–18.53] | 32 |
| 5 | **7.36** [6.80–8.57] | **18.72** [17.29–21.10] | 32 |
| 6 | **8.12** [7.38–9.05] | **19.98** [18.83–22.36] | 31 |
| 8 | **7.96** [6.70–9.14] | **20.83** [19.23–22.81] | 16 |

## Lines: what opening a 64 B line costs, and the shire cache's banks

32 B vector loads through the L1 from the shire's own scratchpad, striding so that every line is filled once and all, half or a quarter of it is used. Energy per *load* rises as the fill is shared by fewer loads; the difference is the cost of the fill itself.

| Stride | Fills per 32 B load | zeros pJ per load [range, three cards] | random pJ per load [range] | zeros pJ/B delivered | random pJ/B delivered |
|---|---|---|---|---|---|
| 32 B | 0.5 | **142.3** [127.1–158.4] | **200.1** [185.2–217.1] | 4.45 | 6.25 |
| 64 B | 1 | **192.6** [172.2–217.5] | **319.2** [294.4–357.3] | 6.02 | 9.98 |
| 128 B | 1 | **193.7** [168.8–230.8] | **318.2** [291.6–364.7] | 6.05 | 9.94 |

Twice the difference between the stride-64 and stride-32 rows is the fill of one 64 B line from the scratchpad into the L1: **101 pJ on zeros, 238 pJ on random data** (aifoundry2 221, aifoundry3 223, aifoundry1 card 1 271 on random data) — 1.6 and 3.7 pJ per byte of line, roughly 65–85% of the 2.1 and 4.4 pJ/B a tensor load pays for the same bytes from the same scratchpad on the three cards; the version-3 check, a separate run, resolved the fill below the tensor load on random data on aifoundry3 (0.80 [0.66, 0.94]) and aifoundry1 card 1 (0.83 [0.69, 0.97]) but not on aifoundry2 (0.77 [0.43, 1.11]), where it is not separable from equal. What random data adds over zeros is about 138 pJ for the line's 512 bits, 269 fJ per bit on the path from the shire cache into the L1. What is left in a 32 B load once its share of the fill is taken out — about 92 pJ on zeros — is the L1 hit itself plus the awake core issuing it.

The same scratchpad read with 64 B tensor loads at strides that cycle the shire cache's banks, alternate two of them, or return to the same one (banks are address bits [7:6], sub-banks [9:8]):

| Stride | zeros pJ per 64 B [range] | random pJ per 64 B [range] | GB/s |
|---|---|---|---|
| 64 B | 266.4 [246.9–291.0] | 424.8 [392.7–451.4] | 923 |
| 128 B | 278.0 [253.9–298.9] | 414.5 [362.0–463.5] | 923 |
| 256 B | 314.0 [282.3–337.3] | 469.1 [427.5–520.3] | 614 |

Coming back to the same bank every time cuts the bandwidth by 33% (614 against 923 GB/s, the same on every card), but what it does to the energy per byte cannot be told apart from the other strides'.

## Rows: does the DRAM row pattern matter?

1 KB tensor loads from DRAM by 32 harts (minion 0 of every shire), each over its own 64 MB, so the touched set beats the 32 MB L3 whatever the pattern. Sequential: consecutive kilobytes go to consecutive banks and each bank sees 32 columns of a row before moving on. Row hit: stride 8 KB, so every access is the next column of the same bank and row. Row miss: after every 8 KB a jump to the next row, so every bank sees a new row on every visit. Thirty-two awake minions are 0.06 W, not worth correcting for.

| Pattern | zeros pJ/B [range over 3 passes on each of three cards] | random pJ/B [range] | GB/s (aifoundry2) |
|---|---|---|---|
| sequential: next bank, 32 columns per row visit | **120.6** [111.2–139.2] | **156.4** [147.2–166.6] | 16.9 |
| same bank and row, next column, every access | **120.4** [105.2–140.9] | **155.9** [142.8–172.3] | 13.9 |
| new row on every visit to a bank | **118.5** [102.5–141.7] | **158.5** [139.7–173.1] | 16.9 |

**The row pattern does not change the energy per byte.** Row hits, row misses and the streaming case agree within their pass-to-pass error on both operand sets, on every card (the version-3 check: no pattern differs at 99% on aifoundry2, aifoundry3 and aifoundry1 card 1). On aifoundry2 the controller runs an open-page policy: a row stays open until a refresh (every 3.87 µs) or an access to another row of its bank closes it ([Anatomy of a memory access](https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy#how-long-a-row-stays-open)). Each hart here comes back to its row only every 1,200–1,400 cycles or so (32 harts at 14–17 GB/s), with 31 other streams in between, and a refresh falls every 2,325 cycles. So either every pattern paid an activation, or an activation is small next to the transfer (one of about 30 pJ/B on zeros, or 50 on random data, would have shown); for a programmer it makes no difference. These 32-hart loads cost 18–20% more per byte than [4.1](04-bytes-memory.md)'s tensor loads at 76 GB/s (25–27% more on zeros); the version-3 check resolved the premium on random data on aifoundry3 and aifoundry1 card 1 but not on aifoundry2: use them to compare patterns, and 4.1 to price DRAM.

An earlier version of this experiment with all 1,024 minions and 32 KB touched per hart fitted in the L3 and measured that instead: **7.6 pJ/B on zeros and 19.3 on random data on aifoundry2, 7.5 and 18.8 on aifoundry3, 9.0 and 22.8 on aifoundry1 card 1, at 1072 GB/s** — the L3, read by tensor loads through the mesh, which the 18 September table put at 10.8 pJ/B at a higher clock.

## Placement inside a shire: which neighbourhood reads

The shire's own scratchpad read by only one of its four neighbourhoods at a time (8 minions each), random data.

| Neighbourhood | pJ/B [range, three cards] | GB/s |
|---|---|---|
| 0 (minions 0–7) | **4.14** [3.62–4.61] | 967 |
| 1 (minions 8–15) | **3.93** [3.43–4.64] | 966 |
| 2 (minions 16–23) | **4.25** [3.64–4.68] | 967 |
| 3 (minions 24–31) | **4.25** [3.76–4.97] | 966 |

## Leakage of the arrays: the SRAM rail against temperature

The SRAM rail during every idle stretch of the session on aifoundry2, against die temperature. The rail feeds the 128 MB of on-chip SRAM (16 MB of L2, 32 MB of L3, 80 MB of scratchpad). Fitted with the idle law's 36 °C e-folding imposed, not fitted:

$$P_\text{SRAM}(T) = -0.26\,\mathrm{W} + 2.76\,\mathrm{W}\; e^{(T-80\,^\circ\mathrm{C})/36\,^\circ\mathrm{C}}$$

- **The negative constant says the rail rises faster than that shape**, so the fitted leakage term is not the arrays' leakage. The whole rail at 80 °C is 2.51 W, **19.6 mW per MB**, an upper bound on the arrays' leakage including the cache logic on the same rail; it rises 77 mW per °C at 80 °C for the whole 128 MB. Measured: 1.70 W at 67 °C, 2.14 W at 75 °C, 2.78 W at 83 °C, 3.47 W at 91 °C.
- This is what the memory costs for existing, per second, at a given die temperature: at about 20 mW per MB a byte held in scratchpad for one second leaks at most about 19 nJ at 80 °C on aifoundry2, as much as reading it 4,200 times (4.4 pJ per read).
- The same rail on aifoundry3 in its idle stretches: 2.17 W at 56 °C, 2.23 W at 57 °C, 2.28 W at 58 °C, 2.33 W at 59 °C; at 58 °C, its most-sampled bin, that is 1.03 W above the aifoundry2 fit extrapolated there.
- The same rail on aifoundry1 card 1 in its idle stretches: 2.33 W at 57 °C, 2.50 W at 62 °C, 2.72 W at 67 °C; at 61 °C, its most-sampled bin, that is 1.10 W above the aifoundry2 fit extrapolated there.

- The aifoundry2 fit does not describe the other cards: in the version-3 idle cycles, heated from about 55 °C into the fit's range, aifoundry3's rail sat 1.03–1.21 W above it at 55–84 °C, rising 0.066 W per °C and aifoundry1 card 1's rail sat 0.99–1.17 W above it at 57–81 °C, rising 0.051 W per °C (against the aifoundry2 law as registered, −0.32 + 2.81 W, from the 23 September catalogue, `catalogue-23sep.json`), so the difference is the card, not the fit's shape outside its range.

| Die °C | SRAM rail W, aifoundry2 | idle stretches | SRAM rail W, aifoundry3 | idle stretches | SRAM rail W, aifoundry1 card 1 | idle stretches |
|---|---|---|---|---|---|---|
| 56 | — | — | 2.174 | 67 | — | — |
| 57 | — | — | 2.227 | 280 | 2.330 | 13 |
| 58 | — | — | 2.275 | 727 | 2.356 | 74 |
| 59 | — | — | 2.329 | 99 | 2.389 | 181 |
| 60 | — | — | — | — | 2.441 | 318 |
| 61 | — | — | — | — | 2.467 | 370 |
| 62 | — | — | — | — | 2.498 | 110 |
| 63 | — | — | — | — | 2.543 | 24 |
| 64 | — | — | — | — | 2.587 | 26 |
| 65 | — | — | — | — | 2.636 | 13 |
| 66 | — | — | — | — | 2.672 | 10 |
| 67 | 1.698 | 6 | — | — | 2.723 | 11 |
| 68 | 1.699 | 19 | — | — | 2.774 | 8 |
| 69 | 1.763 | 17 | — | — | 2.826 | 6 |
| 70 | 1.830 | 72 | — | — | 2.891 | 8 |
| 71 | 1.896 | 180 | — | — | 2.909 | 4 |
| 72 | 1.954 | 196 | — | — | — | — |
| 73 | 2.019 | 86 | — | — | — | — |
| 74 | 2.081 | 111 | — | — | — | — |
| 75 | 2.142 | 232 | — | — | — | — |
| 76 | 2.206 | 66 | — | — | — | — |
| 77 | 2.305 | 11 | — | — | — | — |
| 78 | 2.384 | 15 | — | — | — | — |
| 79 | 2.430 | 9 | — | — | — | — |
| 80 | 2.509 | 11 | — | — | — | — |
| 81 | 2.600 | 11 | — | — | — | — |
| 82 | 2.726 | 7 | — | — | — | — |
| 83 | 2.780 | 9 | — | — | — | — |
| 84 | 2.830 | 8 | — | — | — | — |
| 85 | 2.923 | 7 | — | — | — | — |
| 86 | 3.002 | 15 | — | — | — | — |
| 87 | 3.099 | 14 | — | — | — | — |
| 88 | 3.207 | 23 | — | — | — | — |
| 89 | 3.279 | 21 | — | — | — | — |
| 90 | 3.359 | 14 | — | — | — | — |
| 91 | 3.470 | 15 | — | — | — | — |

## Where the current flows: each class of operation by rail

The PMIC meters three rails — the minions, the on-chip SRAM, and the mesh — and the service processor reports them; board power covers everything including the regulators' own losses. The split of a burst's power over idle across those rails, read from the last 0.6 s of each burst and divided by the 0.94 of the step that the PMIC's running average (time constant 1.13 s on aifoundry2, 1.24 s on aifoundry3 and 1.15 s on aifoundry1 card 1) has reached there, averaged over the instructions in each class on random data, on aifoundry2 (three passes). What is not on a metered rail is the regulators and whatever else has no sensor.

| Class | W over idle | minions | SRAM | mesh | unmetered |
|---|---|---|---|---|---|
| Scalar integer | 4.30 | 79% | 1% | 0% | 20% |
| Scalar multiply | 2.45 | 69% | 3% | -1% | 29% |
| Scalar float | 13.01 | 83% | 2% | 1% | 14% |
| Vector float | 22.57 | 82% | 1% | 1% | 16% |
| Vector integer | 12.07 | 82% | 2% | 1% | 15% |
| Transcendental | 20.17 | 81% | 1% | 1% | 17% |
| L1 hits | 7.12 | 83% | 2% | 1% | 15% |
| L1-bypass to the L2 | 8.15 | 28% | 64% | 1% | 7% |
| Atomics, local L2 | 4.83 | 26% | 63% | 0% | 11% |
| Atomics, home L3 | 3.99 | 26% | 24% | 33% | 17% |
| Own scratchpad, tensor load | 10.19 | 24% | 69% | 1% | 7% |
| Own scratchpad, tensor store | 9.83 | 20% | 76% | 1% | 3% |
| Scratchpad 1 hop away | 13.14 | 14% | 50% | 27% | 10% |
| Scratchpad 3 hops away | 15.28 | 11% | 36% | 40% | 14% |
| Scratchpad 6 hops away | 16.00 | 8% | 26% | 50% | 17% |
| DRAM, tensor load | 10.20 | 2% | 11% | 18% | 69% |
| DRAM, tensor store | 10.34 | 2% | 16% | 19% | 64% |
| DRAM, stores through the L1 | 8.84 | 10% | 12% | 21% | 58% |

**The mesh rail alone**, against hop distance on random data: 1.273 pJ/B per hop with an intercept of 1.44 pJ/B (the cost of leaving the shire). This is the wire and router energy measured on its own supply, independently of the board-power fit above.

| hops | mesh rail, pJ/B |
|---|---|
| 1 | 2.35 |
| 2 | 3.72 |
| 3 | 5.05 |
| 4 | 7.11 |
| 5 | 8.45 |
| 6 | 9.56 |
| 8 | 10.75 |

## What is on no metered rail: attributed, and a droop meter for DRAM

The remainder — board power minus the three rails — cannot be metered with anything on the card, but over the whole catalogue what a workload adds above idle can be attributed: each configuration's mean unmetered watts fitted as a fraction of each rail's watts plus a cost per DRAM byte, no intercept. `tools/ettelem/fit_unmetered.py` makes the fit from `catalogue.json` and writes it to `unmetered_fit.json`. The canonical account of it is [Limits of observability, §4.2–4.3](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#the-unmetered-remainder-attributed); this section keeps the full tables.

| unmetered W of a configuration = | aifoundry2 | aifoundry3 | aifoundry1 card 1 |
|---|---|---|---|
| × minion-rail W | 0.188 ± 0.003 | 0.181 ± 0.002 | 0.102 ± 0.004 |
| × SRAM-rail W | 0.034 ± 0.016 | 0.043 ± 0.015 | 0.540 ± 0.027 |
| × mesh-rail W | 0.291 ± 0.021 | 0.294 ± 0.020 | 0.205 ± 0.026 |
| per DRAM byte | 72.7 ± 1.5 pJ/B | 72.7 ± 1.4 pJ/B | 81.6 ± 2.2 pJ/B |
| residual rms, configuration means | 0.33 W, n = 392 | 0.31 W, n = 392 | 0.48 W, n = 392 |
| residual rms, the configurations that move DRAM | 0.99 W, n = 17 | 0.99 W, n = 17 | 1.19 W, n = 17 |

- **An instruction's unmetered energy is consistent with the regulators' delivery loss**: 19%, 18% and 10% of what the minion rail delivers on aifoundry2, aifoundry3 and aifoundry1 card 1 goes missing between the 12 V input and the core, and nothing else moves; that is as far as the rails' meters can be trusted, since each 1% of error in their scale moves it by about 1.2 points. The 20% "unmetered" share of the scalar integer class above is this.
- **A DRAM byte's unmetered energy is the memory's**: 73–82 pJ per byte on average (the fitted coefficient on the three cards) in the DDR PHY, the I/O rail and the DRAM chips (53–75 on zeros and constants, 77–90 on random data), on top of the 16–66 pJ the mesh, the SRAM and the delivery losses take on the way: together the 95–133 pJ per byte of [4.1](04-bytes-memory.md)'s tensor loads from DRAM. A byte written through the L1 costs about twice that off-rail (114–187 pJ), because the line is read from DRAM before it is written.
- **The residual on the configurations that move DRAM is 24–25% of their unmetered power (rms over mean), and it has a pattern**: stores through the L1 sit 1.1–2.8 W above the fit, because the line read from DRAM before each store is not in their byte count; the tensor loads and stores from DRAM and the 1,024-minion DRAM loads sit above it on random data (+-0.3 to +0.9 W) and below it on zeros and constants (−0.4 to −1.5 W). The published fit is kept as it is; counting those line reads (the stores' bytes twice) would bring the DRAM residual to 0.67 W on aifoundry2 (DRAM term 69.9 pJ/B) and 0.68 W on aifoundry3 (DRAM term 69.8 pJ/B) and 0.73 W on aifoundry1-c1 (DRAM term 78.8 pJ/B); that refit is `l1_line_read_refit` in `unmetered_fit.json`.
- **The mesh coefficient is not all regulator**: 29% is too much for a delivery loss; the memory shires' own logic, on an unmetered rail, works whenever the mesh moves bytes to them.
- What the fit cannot say: how the idle 12–18 W (12–13 W on aifoundry3 at 55–60 °C, 12–17 W on aifoundry1 card 1 at 57–71 °C, 14–18 W on aifoundry2 at 67–92 °C) splits between DDR, PCIe, the IO shire, Maxion and the regulators' own draw, or how the DRAM term splits below its regulator. That is the subject of the improvement ladder in [Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability).

**A droop meter for DRAM.** The memory shires' Moortec voltage monitors report the 0.8 V DDR rail once per service-processor pass (about every 156 ms on aifoundry2, 263 ms on aifoundry3 and 158 ms on aifoundry1 card 1 under the 10 Hz sampler; `die_mv.ddr` in every telemetry file; 767 mV at idle against an 800 mV set point). Across the 392 configuration means it droops **0.86 mV per watt of off-rail DRAM power** (plus 0.034 mV per watt of anything else; rms 0.35 mV): 1 mV ≈ 1.2 W of DRAM, refreshed every pass, from a sensor that was always there. It is a proxy calibrated against the fit above, not a meter, and not independent of the board meter. It responds mostly to DRAM traffic, but not only: heavy mesh and scratchpad traffic with no DRAM access droops it too, by up to 2.0 mV, and 2.0 mV for L3 reads through the mesh (`fmadd.ps/random/h2` 0.99 mV and `tload/scp/random` 2.00 mV and `wire/hop6/random` 1.00 mV in the table below), which it would read as up to about 1.9 W of DRAM; and its idle reading moves by about 1 mV between 71 and 77 °C. The minion rail sags 0.053 mV per watt the cores draw; the [Power and temperature](https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature) report (§3) maps each shire's rails at idle.

| Configuration (aifoundry2, mean of three passes) | W over idle | unmetered W less the fitted rail losses | DDR-rail droop, mV | minion-rail droop, mV |
|---|---|---|---|---|
| `add/zeros/h2` | 2.95 | — | 0.02 | 0.00 |
| `fmadd.ps/random/h2` | 24.82 | — | 0.99 | 1.02 |
| `st_stream/dram/random` | 8.84 | 4.39 | 4.48 | 0.00 |
| `tload/dram/random` | 10.20 | 6.38 | 5.53 | 0.00 |
| `tload/dram/zeros` | 6.88 | 4.77 | 3.00 | 0.00 |
| `tload/scp/random` | 10.19 | — | 2.00 | 0.00 |
| `tstore/dram/random` | 10.34 | 5.92 | 5.90 | 0.00 |
| `wire/hop6/random` | 16.00 | — | 1.00 | 0.22 |


Sources: `docs/reports/data/2026-09-25-claims-v3/raw/<card>/catfull/` (the version-3 full catalogue, 26 September), reduced by `tools/claims-v3/catfull/reduce.py` (which cuts the bursts with `workloads/enercat/analyze_catalogue.py`'s own code) into `docs/reports/data/2026-09-23-energy-manual/catalogue.json`; the attribution and the droop in `unmetered_fit.json` beside it, written by `tools/ettelem/fit_unmetered.py`; the version-3 check's per-card tests from `manual.json` (v3). The 23 September catalogue it replaces is `catalogue-23sep.json` in the same directory.

