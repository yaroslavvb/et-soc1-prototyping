# The ET-SoC-1 energy manual

What every kind of operation on this card costs in joules, arranged so that a workload's energy can be built
up from parts, with every number traceable to the measurement that produced it.

**Every repeated measurement carries a confidence bar** — mean [lo–hi] over repeated passes on three cards (aifoundry2, aifoundry3 and aifoundry1's card 1, in the version-3 check of 26 September 2026), with each card's own mean ± standard error beside it; rows measured once, or derived, say so. A figure with no card named held on every card (three passes or more on each, or the same value on each); where one rests on one card, on fewer runs, or differs between the cards, the text says so. What the instruments can and cannot see, and what would let them see more, is the companion [limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability), which also has the glossary (minion, hart, shire, scratchpad, PMIC). The published page is <https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual>.

**Start with [00-structure.md](00-structure.md)** for the equation and the conventions. Then:

| § | Page | The one number to remember |
|---|---|---|
| 1 | [The card at rest](01-at-rest.md) | on aifoundry2, 35.9 W idle at 80 °C and 0.65 W more per °C; 20–29 W of it leakage (the idle bins do not pin the split closer); aifoundry3 idles 1.0 W above that law and aifoundry1's card 1 10.1 W above it |
| 2 | [A core that is awake](02-awake.md) | 1.9 mW per minion awake on one hart, 3.0 on two; one stalled on a contended atomic draws 1.2 mW |
| 3 | [Instructions](03-instructions.md) | integer add 6 pJ on zeros (10 random), float add 24 pJ, 8-lane FMA 27 pJ on zeros and 56 on random data; a tensor multiply-add 0.3 pJ on zeros, 5.8 on random |
| 3.1 | [Every instruction](03a-every-instruction.md) | all 161 instructions the silicon executes in U-mode, and the 15 gather, scatter and packed-atomic instructions of E48 from the L1 (a word gather 104 pJ, 13 per element), three shuffled passes on each of three cards: cheapest `fence` and `auipc` (4.5–5.3 pJ on random data), dearest the global atomics `amoaddg.w` and `.d` (about 1,380 pJ), pooled over the cards; pass-to-pass standard error 2.1% in the median on aifoundry2, 1.4% on aifoundry3, 1.5% on aifoundry1's card 1; aifoundry3 at 0.972× and aifoundry1's card 1 at 0.962× aifoundry2 over all 392 configurations, each at its own die temperature |
| 4 | [Bytes through memory](04-bytes-memory.md) | L1 hit 0.5 pJ/B, own scratchpad 2–9 pJ/B, DRAM 95–140 pJ/B; writes through the L1 to DRAM 250–340 pJ/B |
| 4.4 | [Irregular access: gathers and scatters by level](04-bytes-memory.md#44-irregular-access-gathers-and-scatters-by-level-e48-26-september-three-passes-on-each-of-three-cards) | a random 4 B element by `fgw.ps` gather: 12.8 pJ from the L1 (452 G/s over the chip, what a scalar load costs), 354 pJ from the L2 (27.4 G/s, 29× the same bytes streamed), 9.8 nJ from DRAM (1.19 G/s, 19×); a scatter costs about twice a gather past the L1 (E48, three passes on each of three cards) |
| 4.3 | [Finer grain: wires, lines, rows, leakage](04a-fine-grain.md) | one mesh hop costs 1.7–1.9 pJ/B on random data and 0.6–0.7 on zeros, fitted over 1–8 hops; over 1–6 hops, leaving out the 8-hop point only 16 shires reach, 2.2–2.4 pJ/B, which is what [Heat per millimetre](https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm) measures (use its figures for wires; it also separates flips from ones carried); filling a 64 B line into the L1 is about 100 pJ on zeros and 240 on random data; the DRAM row pattern does not change the energy on any card; the SRAM rail idles at 1.7 W at 67 °C and 2.7 W at 82 °C on aifoundry2, about 1 W more on the other cards; where each class's current flows, by rail; the unmetered remainder attributed (10–19% delivery loss on the minion rail, 73–82 pJ per DRAM byte off-rail) and a droop meter for DRAM, in full here; the canonical account is [Limits of observability, §4.2–4.3](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#the-unmetered-remainder-attributed) |
| 5 | [Bytes between cores](05-bytes-between-cores.md) | under 1 pJ/B between the two minions of a pair, 2 around a neighbourhood or a shire, 12–18 across the mesh (about 9 pJ to leave the shire plus 1.75 per mesh hop, the same on every card); 8.6, 8.3 and 9.9 pJ/B on aifoundry2, aifoundry3 and aifoundry1's card 1 to hand a slab to the next shire, 13× less than the DRAM round trip on every card |
| 6 | [Synchronisation](06-synchronisation.md) | a contended atomic 20 nJ [17–24]; a spread one 1.2 nJ; a chip barrier is 5,000 cycles of leakage; a packed atomic add `famoaddl.pi` 0.39 nJ per update at 12.7 G/s, no faster than scalar `amoaddl.w` (0.27 nJ); gather-add-scatter 0.036 nJ per update in the L1 at 139 G/s |
| 7 | [Composition](07-composition.md) | a dense matmul at 80 °C on aifoundry2 is 57% static energy (the published page prices any mix of rows at any die temperature, on each card with its own idle law); priced from §4 after the fact, the relay falls inside its wide brackets through DRAM and the next shire and at the low edge of its bracket (5% below, within noise) through its own scratchpad |
| 8 | [Card-to-card variation](08-cards.md) | aifoundry3 reads 0.97× aifoundry2 in the median (10–90%: 0.92–1.00), which its cooler die accounts for (the energy per operation rises 0.3–0.5% per °C); aifoundry1's card 1 reads 0.95× per instruction but 1.15× per byte, in line with its lower minion and higher SRAM rail voltage |
| 9 | [Method and limits](09-method.md) | how each number was made, how the bars were made (three passes on each of three cards; warm die; bursts that moved the clock dropped, and in the reruns bursts that starved the sampler; the catalogue keeps the DRAM-read bursts that slowed it), and what it cannot tell you |

Everything is at **600 MHz** (the minion rail at 0.52 V), the point the governor pins a warm card to, unless stated.

## Regenerating

```
npm ci    # once: mathjax-full 3.2.1, pinned in package.json, for build-report.py's TeX
python3 workloads/enercat/analyze_enercat.py docs/reports/data/2026-09-23-enercat-aifoundry2 docs/reports/data/2026-09-23-enercat-aifoundry3 --out docs/reports/data/2026-09-23-energy-manual/enercat.json
python3 tools/claims-v3/catfull/reduce.py --data docs/reports/data/2026-09-25-claims-v3/raw --out /tmp/catfull-verdicts.json --catalogue-out docs/reports/data/2026-09-23-energy-manual/catalogue.json --cards aifoundry2,aifoundry3,aifoundry1-c1
python3 tools/ettelem/analyze_reruns.py docs/reports/data/2026-09-23-reruns-aifoundry2-warm docs/reports/data/2026-09-23-reruns-aifoundry3 --v3-rl docs/reports/data/2026-09-25-claims-v3/raw --out docs/reports/data/2026-09-23-energy-manual/reruns.json
python3 tools/ettelem/fit_unmetered.py --out docs/reports/data/2026-09-23-energy-manual/unmetered_fit.json --overwrite
python3 tools/ettelem/build_energy_manual.py --out docs/reports/data/2026-09-23-energy-manual/manual.json
python3 tools/ettelem/render_energy_manual.py docs/reports/data/2026-09-23-energy-manual/manual.json docs/energy-manual/
python3 tools/ettelem/render_catalogue.py docs/reports/data/2026-09-23-energy-manual/catalogue.json docs/energy-manual/
python3 scripts/build-report.py energy-manual docs/reports/data/2026-09-23-energy-manual/manual.json docs/reports/2026-09-23-energy-manual.html
```

The first four reduce the raw runs. Since 26 September the catalogue is the version-3 check's full catalogue on three
cards (V3-CATFULL, `tools/claims-v3/catfull/`: its reducer cuts the bursts with `analyze_catalogue.py`'s own code and
writes `catalogue.json` in that tool's shape), and the relay, rings and levels are its V3-RL passes (`--v3-rl`); the hot
line keeps the 23 September reruns. The 23 September catalogue is kept as `catalogue-23sep.json` (the version-3
reducers read it as a registered input; `analyze_catalogue.py` on the three `2026-09-23-catalogue-*` directories
reproduces it). The card-side runners (`run_enercat.sh`, `run_catalogue.py`, `run_reruns_warm.sh`,
`run_rl_warm_a2.sh`, `run_rings_levels_power.sh` and `tools/claims-v3/*/block.sh`) are in
docs/findings/03-experiments.md (E26–E29 and the version-3 check); `fit_unmetered.py` fits the attribution of the unmetered power and the DDR droop meter and writes
`unmetered_fit.json`. `build_energy_manual.py` then collects every table from its data file (the JSON records which,
including the hot-line, relay, DVFS and Horace files that their own reports' pipelines write); the next two render
the pages 01–06, 08, 03a and 04a from the data, so a number there is never typed by hand; the last builds the
published page. This README, 00, 07 and 09 are written by hand. The instruction catalogue itself is
`workloads/enercat`: `run_catalogue.py` measures (three shuffled passes), `analyze_catalogue.py` reduces.

Published: <https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual>. Provenance: `docs/findings/`.

Version 3 (25 September): every claim checked for proof on both cards; the idle law is led by its measured slope,
with its split into fixed and leakage given as a range; figures that rest on one card, on fewer than three runs,
or that differ between the cards say so; rankings and differences within the noise removed. The record is
`docs/reports/data/2026-09-25-claims-v3/`.

26 September: the version-3 check's three-card measurements (aifoundry1's card 1 joins aifoundry2 and aifoundry3)
replace the catalogue, the rings, the levels, the relay and the tensor rows, and add each card's idle; 52 of the
published page's claims were re-measured under a pre-registered plan (the page's note lists the outcome).

27 September: the gathers, scatters and packed atomics measured on the same three cards after the check (E48,
`docs/reports/data/2026-09-25-claims-v3/results/gs.json` and `gs-full.json`), pooled into `manual.json` `gs` by
`build_energy_manual.py` and rendered into 3.1 (the L1 rows), 4.3 (patterns, masks, element sizes), a new 4.4
(irregular access by level) and 6 (the packed atomics and scatter-add); the rows come from `tools/ettelem/gs_levels.py`.
