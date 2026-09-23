# 1. The card at rest

What the card draws when nothing is running. Every joule in the rest of the manual is *above* this.

## The law

$$P_\text{idle}(T) = 12.6\,\mathrm{W} + 23.3\,\mathrm{W}\; e^{(T-80\,^\circ\mathrm{C})/36\,^\circ\mathrm{C}}$$

- **12.6 W is temperature-independent**: PCIe, the DDR PHY, the IO shire, regulators, clocks. It does not respond to anything a kernel does.
- **The rest is leakage**, 23.3 W at 80 °C, e-folding every 36 °C, so its slope at 80 °C is 0.65 W per °C. This is the term a workload controls, by setting the temperature.
- Fitted on 21 September to every idle sample of five hours of sessions (rms 0.20 W from 64 to 88 °C); predicted a 20-hour idle the next day to +0.01 W; extrapolated 25 °C below its range onto aifoundry3 to +0.73 W. Source: `docs/reports/data/2026-09-21-horace-aifoundry2/model.json`.

| Die °C | Idle W | Leakage share |
|---|---|---|
| 40 | 20.3 | 38% |
| 50 | 22.7 | 44% |
| 60 | 26.0 | 51% |
| 70 | 30.3 | 58% |
| 80 | 35.9 | 65% |
| 90 | 43.3 | 71% |

## Where idle goes, by rail (73 °C, 20 hours idle)

| Rail | W | Share |
|---|---|---|
| Minions | 11.05 | 35% |
| SRAM (L2, L3, scratchpad) | 2.00 | 6% |
| Mesh | 3.64 | 11% |
| **No rail sensor** (PCIe, DDR, IO shire, regulators) | **15.10** | 48% |
| Board | 31.79 | |

The three sensed rails are the service processor's own ~2 s averages; the unsensed remainder is board power minus their sum. Source: `docs/reports/data/2026-09-22-dvfs-aifoundry2/dvfs.json`.

## Operating points

| MHz | Minion V | Relative switching power (V²f) |
|---|---|---|
| 600 | 0.517 | 1.00× |
| 700 | 0.568 | 1.41× |
| 800 | 0.618 | 1.91× |

A warm card (above 65 °C) is pinned to the first row by the governor; every table in this manual is at that point unless it says otherwise. The other two are reached only from a cool start (docs/findings/16-dvfs-and-leakage.md).

## The two working cards

| | aifoundry2 | aifoundry3 |
|---|---|---|
| Static TDP the firmware uses | 65 W | **0 W** (pinned at 600 MHz for life) |
| Minion voltage at 600 MHz | 518 mV | 523 mV |
| Typical idle | 31–36 W at 73–80 °C | 23.6 W at 51 °C |
