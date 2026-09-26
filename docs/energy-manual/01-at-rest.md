# 1. The card at rest

What the card draws when nothing is running. Every joule in the rest of the manual is *above* this.

## The law

$$P_\text{idle}(T) = 12.6\,\mathrm{W} + 23.3\,\mathrm{W}\; e^{(T-80\,^\circ\mathrm{C})/36\,^\circ\mathrm{C}}$$

- **What the idle measurements pin down is the slope.** On aifoundry2 the idle card draws 35.9 W at 80 °C and 0.65 W more for each degree there (0.64–0.65 W per °C for every e-folding that fits). This is the term a workload controls, by setting the temperature.
- **How much of it is leakage they do not.** The idle bins fit equally well with the leakage e-folding anywhere from 30 to 45 °C (doubling every 21–31 °C), which puts the leakage at 80 °C at 20–29 W and the fixed part at 7–16 W. The law above is the best fit, 12.6 W fixed and 23.3 W of leakage at 80 °C e-folding every 36 °C: a fit, not a block-by-block account.
- **The blocks with no rail sensor** (PCIe, the DDR PHY, the IO shire, the regulators) draw about 15 W on aifoundry2 (67–92 °C), 13 W on aifoundry3 (55–60 °C) and 16 W on aifoundry1 card 1 (57–71 °C) at idle in the catalogue's idle stretches, and move little with temperature: 0.10 [0.06–0.15] W per °C over 74–88 °C on aifoundry2 in the version-3 idle cycles (26 September, three per card; 99% intervals), 0.07 on aifoundry3 and 0.16 [0.08–0.24] on aifoundry1 card 1. The three metered rails carry the leakage, 0.53 [0.50–0.55] W per °C between them at 75–80 °C on aifoundry2 (0.77 [0.76–0.78] on aifoundry1 card 1). What the unsensed blocks spend when a kernel uses them (DRAM traffic through the DDR PHY, the regulators' delivery loss) is counted in the per-event costs of the later sections; [4.3](04a-fine-grain.md) attributes it.
- **Confidence.** Fitted on 21 September to every idle sample of five hours of sessions on aifoundry2, rms 0.20 W from 64 to 88 °C (bins 64–67 and 81–88 °C). Checked two ways: it predicted the idle 20.6 hours after the last workload (apart from a 4.9 s single-hart probe a few minutes before), the next day, to +0.01 W (300 samples over a minute, sd 0.04 W); and in the version-3 check's idle cycles (26 September: three heat-and-cool cycles per card, every sample at 600 MHz) aifoundry2 sat +0.04 W [−0.15, +0.22] from the law at 67–83 °C; aifoundry3 +1.01 W [+0.95, +1.07] at 54–84 °C, the gap growing 0.036 W per °C; and aifoundry1 card 1 +10.07 W [+9.73, +10.40] at 56–81 °C, the gap growing 0.237 W per °C. The law holds on aifoundry2 to a tenth of a watt; the other two cards idle above it, and [7](07-composition.md) prices each with its own law (the same form refitted to its cycles, e-folding held at 36 °C: aifoundry3 12.3 W + 25.0 W·e^((T−80)/36), rms 0.10 W and aifoundry1 card 1 14.1 W + 34.8 W·e^((T−80)/36), rms 0.09 W). Source: `docs/reports/data/2026-09-21-horace-aifoundry2/model.json`, `docs/reports/data/2026-09-25-claims-v3/results/idle.json`.

| Die °C | Idle W, best fit | Leakage share, best fit | Leakage share, e-folding 30–45 °C |
|---|---|---|---|
| 40 | 20.3 | 38% | 24–62% |
| 50 | 22.7 | 44% | 31–67% |
| 60 | 26.0 | 51% | 38–72% |
| 70 | 30.3 | 58% | 46–76% |
| 80 | 35.9 | 65% | 55–80% |
| 90 | 43.3 | 71% | 63–83% |

The fitted bins run from 64 to 88 °C; the other rows are the law extrapolated, where the e-foldings that fit differ by up to 2.4 W in the idle itself.

## Where idle goes, by rail (73 °C)

| Rail | aifoundry2, 22 Sep, W | Share | aifoundry2, 26 Sep (two cycles) | aifoundry1 card 1, 26 Sep (three cycles) |
|---|---|---|---|---|
| Minions | 11.05 | 35% | 11.07 | 15.96 |
| SRAM (L2, L3, scratchpad) | 2.00 | 6% | 1.99 | 3.05 |
| Mesh | 3.64 | 11% | 3.62 | 5.83 |
| **No rail sensor** (PCIe, DDR, IO shire, regulators) | 15.10 | 48% | 15.05 | 17.87 |
| Board | 31.79 ± 0.04 | | 31.73 | 42.71 |

The three sensed rails are the PMIC's own running averages (roughly first-order, time constant 1.13 s on aifoundry2, 1.24 s on aifoundry3 and 1.15 s on aifoundry1 card 1), which the service processor reports; the unsensed remainder is board power minus their sum. The 22 September sample is aifoundry2, 20.6 hours after the last workload apart from a 4.9 s single-hart probe a few minutes before; the board figure's ± is the sd of its 300 samples, taken over one minute; the rails' sd is 0.01 W or less. The 26 September columns are the 73 °C bin of the version-3 idle cycles, which two of aifoundry2's three and all three of aifoundry1 card 1's reached; aifoundry2's agree with 22 September to within 0.05 W but come from two cycles, one short of the three the check needed, so the split is not confirmed there; aifoundry1 card 1 draws 10.9 W more, on every rail. Source: `docs/reports/data/2026-09-22-dvfs-aifoundry2/dvfs.json`, `docs/reports/data/2026-09-25-claims-v3/results/idle.json`. The SRAM rail's own temperature law, on every card, is in [4.3](04a-fine-grain.md).

## Operating points

| MHz | Minion V | Relative switching power (V²f) |
|---|---|---|
| 600 | 0.517 | 1.00× |
| 700 | 0.568 | 1.41× |
| 800 | 0.618 | 1.91× |

A warm card is held at the first row by the governor, which steps down when the whole-degree die reading is above 65 °C or board power is above 65 W; every table in this manual is at that point unless it says otherwise. The other two are reached only from a cool start (docs/findings/16-dvfs-and-leakage.md); aifoundry3, whose firmware reports a TDP of 0 W, never leaves 600 MHz; aifoundry1's card 1 (firmware 1.2.0) reports 65 W like aifoundry2 and sat at 600 MHz in every sample of the version-3 check. **On a cooler die the governor lifts the clock in the middle of a burst** (below about 68 °C of the sampler's mean reading, so the reruns preheat the die to 76 °C): the first attempt at the reruns of section 5 and 6 on aifoundry2 (12:51–13:10 on 23 September, die 65 °C) had 700–800 MHz excursions in a fifth of its samples and was discarded; the bars in this manual are from bursts at 600 MHz throughout.

## The three cards

| | aifoundry2 | aifoundry3 | aifoundry1 card 1 |
|---|---|---|---|
| Firmware | 1.3.1 | 1.3.1 | 1.2.0 |
| Static TDP the firmware uses | 65 W | **0 W** (pinned at 600 MHz for life) | 65 W |
| Power state at rest | managed_power | max_power | managed_power |
| Minion voltage at 600 MHz | 518 mV | 523 mV | 499 mV |
| Idle during the catalogue (26 September; mean board power, die range) | 32.8 W at 67–92 °C | 25.8 W at 55–60 °C | 34.3 W at 57–71 °C |
