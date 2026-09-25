# 1. The card at rest

What the card draws when nothing is running. Every joule in the rest of the manual is *above* this.

## The law

$$P_\text{idle}(T) = 12.6\,\mathrm{W} + 23.3\,\mathrm{W}\; e^{(T-80\,^\circ\mathrm{C})/36\,^\circ\mathrm{C}}$$

- **What the idle measurements pin down is the slope.** On aifoundry2 the idle card draws 35.9 W at 80 °C and 0.65 W more for each degree there (0.64–0.65 W per °C for every e-folding that fits). This is the term a workload controls, by setting the temperature.
- **How much of it is leakage they do not.** The idle bins fit equally well with the leakage e-folding anywhere from 30 to 45 °C (doubling every 21–31 °C), which puts the leakage at 80 °C at 20–29 W and the fixed part at 7–16 W. The law above is the best fit, 12.6 W fixed and 23.3 W of leakage at 80 °C e-folding every 36 °C: a fit, not a block-by-block account.
- **The blocks with no rail sensor** (PCIe, the DDR PHY, the IO shire, the regulators) draw about 15 W at idle on aifoundry2 (66–82 °C) and 13 W on aifoundry3 (51–56 °C), and barely move with temperature: 0.03 W per °C over 71–83 °C in the catalogue's idle gaps. The three metered rails carry the leakage, 0.55 W per °C between them at about 75 °C. What the unsensed blocks spend when a kernel uses them (DRAM traffic through the DDR PHY, the regulators' delivery loss) is counted in the per-event costs of the later sections; [4.3](04a-fine-grain.md) attributes it.
- **Confidence.** Fitted on 21 September to every idle sample of five hours of sessions on aifoundry2, rms 0.20 W from 64 to 88 °C. Checked two ways: it predicted the idle 20.6 hours after the last workload (apart from a 4.9 s single-hart probe a few minutes before), the next day, to +0.01 W (300 samples over a minute, sd 0.04 W); extrapolated 7–14 °C below its fitted range onto aifoundry3 it was +0.73 W off (rms 0.74 W over 3,596 samples at 50–57 °C). In the idle stretches of the 23 September catalogue, three passes on each card, aifoundry3 sat +0.61 W from the law at 51–56 °C and aifoundry2 −0.23 W at 66–82 °C: the law holds on aifoundry2 to a few tenths of a watt and reads about 3% low on aifoundry3. Source: `docs/reports/data/2026-09-21-horace-aifoundry2/model.json`.

| Die °C | Idle W, best fit | Leakage share, best fit | Leakage share, e-folding 30–45 °C |
|---|---|---|---|
| 40 | 20.3 | 38% | 24–62% |
| 50 | 22.7 | 44% | 31–67% |
| 60 | 26.0 | 51% | 38–72% |
| 70 | 30.3 | 58% | 46–76% |
| 80 | 35.9 | 65% | 55–80% |
| 90 | 43.3 | 71% | 63–83% |

The fitted bins run from 64 to 88 °C; the other rows are the law extrapolated, where the e-foldings that fit differ by up to 2.4 W in the idle itself.

## Where idle goes, by rail (73 °C, 20.6 hours after the last workload)

| Rail | W | Share |
|---|---|---|
| Minions | 11.05 | 35% |
| SRAM (L2, L3, scratchpad) | 2.00 | 6% |
| Mesh | 3.64 | 11% |
| **No rail sensor** (PCIe, DDR, IO shire, regulators) | **15.10** | 48% |
| Board | 31.79 ± 0.04 | |

The three sensed rails are the PMIC's own running averages (roughly first-order, time constant 1.15 s on aifoundry2 and 1.22 s on aifoundry3), which the service processor reports; the unsensed remainder is board power minus their sum. The sample is aifoundry2 on 22 September, 20.6 hours after the last workload apart from a 4.9 s single-hart probe a few minutes before; the board figure's ± is the sd of its 300 samples, taken over one minute; the rails' sd is 0.01 W or less. Source: `docs/reports/data/2026-09-22-dvfs-aifoundry2/dvfs.json`. The SRAM rail's own temperature law, on both cards, is in [4.3](04a-fine-grain.md).

## Operating points

| MHz | Minion V | Relative switching power (V²f) |
|---|---|---|
| 600 | 0.517 | 1.00× |
| 700 | 0.568 | 1.41× |
| 800 | 0.618 | 1.91× |

A warm card is held at the first row by the governor, which steps down when the whole-degree die reading is above 65 °C or board power is above 65 W; every table in this manual is at that point unless it says otherwise. The other two are reached only from a cool start (docs/findings/16-dvfs-and-leakage.md), and aifoundry3, whose firmware reports a TDP of 0 W, never leaves 600 MHz. **On a cooler die the governor lifts the clock in the middle of a burst** (below about 68 °C of the sampler's mean reading, so the reruns preheat the die to 76 °C): the first attempt at the reruns of section 5 and 6 on aifoundry2 (12:51–13:10 on 23 September, die 65 °C) had 700–800 MHz excursions in a fifth of its samples and was discarded; the bars in this manual are from bursts at 600 MHz throughout.

## The two working cards

| | aifoundry2 | aifoundry3 |
|---|---|---|
| Static TDP the firmware uses | 65 W | **0 W** (pinned at 600 MHz for life) |
| Minion voltage at 600 MHz | 518 mV | 523 mV |
| Idle during the 23 September catalogue (catalogue.json bursts) | 31–37 W at 71–82 °C | 23.6–25.0 W at 51–56 °C |
