# The ET-SoC-1 energy manual

What every kind of operation on this card costs in joules, arranged so that a workload's energy can be built
up from parts, with every number traceable to the measurement that produced it.

**Every repeated measurement carries a confidence bar** — mean [lo–hi] over repeated passes on two cards, with each card's own mean ± standard error beside it; rows measured once, or derived, say so. What the instruments can and cannot see, and what would let them see more, is the companion [limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability), which also has the glossary (minion, hart, shire, scratchpad, PMIC). The published page is <https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual>.

**Start with [00-structure.md](00-structure.md)** for the equation and the conventions. Then:

| § | Page | The one number to remember |
|---|---|---|
| 1 | [The card at rest](01-at-rest.md) | 12.6 W fixed plus 23.3 W of leakage at 80 °C, e-folding every 36 °C |
| 2 | [A core that is awake](02-awake.md) | 2 mW per minion awake on one hart, 3.4 on two; one stalled on a contended atomic draws 1.2 mW |
| 3 | [Instructions](03-instructions.md) | integer add 6 pJ on zeros (9 random), float add 23 pJ, 8-lane FMA 27 pJ on zeros and 56 on random data; a tensor multiply-add 0.4 pJ on zeros, 5.8 on random |
| 3.1 | [Every instruction](03a-every-instruction.md) | all 161 instructions the silicon executes in U-mode, three shuffled passes on two cards: cheapest `fence` at 4.5 pJ, dearest `amoaddg.d` at 1,393 pJ (pooled over both cards); pass-to-pass standard error 1.8% in the median; the second card at 0.950× over all 386 configurations |
| 4 | [Bytes through memory](04-bytes-memory.md) | L1 hit 0.5 pJ/B, own scratchpad 2–8 pJ/B, DRAM 90–140 pJ/B; writes through the L1 to DRAM 240–330 pJ/B |
| 4.3 | [Finer grain: wires, lines, rows, leakage](04a-fine-grain.md) | one mesh hop costs 1.7–1.8 pJ/B on random data and 0.6–0.75 on zeros, fitted over 1–8 hops; over 1–6 hops, leaving out the 8-hop point only 16 shires reach, 2.1–2.3 pJ/B, which is what [Heat per millimetre](https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm) measures (use its figures for wires; it also separates flips from ones carried); filling a 64 B line into the L1 is about 100 pJ on zeros and 205 on random data; the DRAM row pattern does not change the energy; the SRAM rail idles at 1.6 W at 67 °C and 2.6 W at 82 °C; where each class's current flows, by rail; the unmetered remainder attributed (18–20% delivery loss on the minion rail, 68–73 pJ per DRAM byte off-rail) and a droop meter for DRAM, in full here; the canonical account is [Limits of observability, §4.2–4.3](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#the-unmetered-remainder-attributed) |
| 5 | [Bytes between cores](05-bytes-between-cores.md) | under 1 pJ/B between the two minions of a pair, 2 around a neighbourhood or a shire, 12–18 across the mesh (about 9 to leave the shire plus 1.7 per mesh hop); 8.6 pJ/B to hand a slab to the next shire, a twelfth of the DRAM round trip |
| 6 | [Synchronisation](06-synchronisation.md) | a contended atomic 20 nJ [17–24]; a spread one 1.2 nJ; a chip barrier is 5,000 cycles of leakage |
| 7 | [Composition](07-composition.md) | a dense matmul at 80 °C is 57% static energy (the published page prices any mix of rows at any die temperature); priced from §4, the relay falls inside its brackets through DRAM and the next shire and 8% below through its own scratchpad |
| 8 | [Card-to-card variation](08-cards.md) | the second card reads 0.95× the first in the median (10–90%: 0.91–0.99) |
| 9 | [Method and limits](09-method.md) | how each number was made, how the bars were made (three passes on two cards; warm die; bursts that moved the clock dropped, and in the reruns bursts that starved the sampler; the catalogue keeps the aifoundry2 DRAM-read bursts that slowed it), and what it cannot tell you |

Everything is at **600 MHz** (the minion rail at 0.52 V), the point the governor pins a warm card to, unless stated.

## Regenerating

```
npm ci    # once: mathjax-full 3.2.1, pinned in package.json, for build-report.py's TeX
python3 workloads/enercat/analyze_enercat.py docs/reports/data/2026-09-23-enercat-aifoundry2 docs/reports/data/2026-09-23-enercat-aifoundry3 --out docs/reports/data/2026-09-23-energy-manual/enercat.json
python3 workloads/enercat/analyze_catalogue.py docs/reports/data/2026-09-23-catalogue-aifoundry2 docs/reports/data/2026-09-23-catalogue-aifoundry3 docs/reports/data/2026-09-23-catalogue-aifoundry2-rows --out docs/reports/data/2026-09-23-energy-manual/catalogue.json
python3 tools/ettelem/analyze_reruns.py docs/reports/data/2026-09-23-reruns-aifoundry2-warm docs/reports/data/2026-09-23-reruns-aifoundry3 --out docs/reports/data/2026-09-23-energy-manual/reruns.json
python3 tools/ettelem/fit_unmetered.py --out docs/reports/data/2026-09-23-energy-manual/unmetered_fit.json --overwrite
python3 tools/ettelem/build_energy_manual.py --out docs/reports/data/2026-09-23-energy-manual/manual.json
python3 tools/ettelem/render_energy_manual.py docs/reports/data/2026-09-23-energy-manual/manual.json docs/energy-manual/
python3 tools/ettelem/render_catalogue.py docs/reports/data/2026-09-23-energy-manual/catalogue.json docs/energy-manual/
python3 scripts/build-report.py energy-manual docs/reports/data/2026-09-23-energy-manual/manual.json docs/reports/2026-09-23-energy-manual.html
```

The first four reduce the raw runs (the card-side runners, `run_enercat.sh`, `run_catalogue.py`,
`run_reruns_warm.sh`, `run_rl_warm_a2.sh` and `run_rings_levels_power.sh`, are in docs/findings/03-experiments.md,
E26–E29); `fit_unmetered.py` fits the attribution of the unmetered power and the DDR droop meter and writes
`unmetered_fit.json`. `build_energy_manual.py` then collects every table from its data file (the JSON records which,
including the hot-line, relay, DVFS and Horace files that their own reports' pipelines write); the next two render
the pages 01–06, 08, 03a and 04a from the data, so a number there is never typed by hand; the last builds the
published page. This README, 00, 07 and 09 are written by hand. The instruction catalogue itself is
`workloads/enercat`: `run_catalogue.py` measures (three shuffled passes), `analyze_catalogue.py` reduces.

Published: <https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual>. Provenance: `docs/findings/`.
