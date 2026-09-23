# The ET-SoC-1 energy manual

What every kind of operation on this card costs in joules, arranged so that a workload's energy can be built
up from parts, with every number traceable to the measurement that produced it.

**Third edition (23 September 2026): every entry carries a confidence bar** — mean [lo–hi] over repeated passes on two cards, with each card's own mean ± standard error beside it. What the instruments can and cannot see, and what would let them see more, is the companion [limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability).

**Start with [00-structure.md](00-structure.md)** for the equation and the conventions. Then:

| § | Page | The one number to remember |
|---|---|---|
| 1 | [The card at rest](01-at-rest.md) | 12.6 W fixed plus 23.3 W of leakage at 80 °C, e-folding every 36 °C |
| 2 | [A core that is awake](02-awake.md) | 2 mW per minion awake; a stalled one costs the same |
| 3 | [Instructions](03-instructions.md) | integer add 7 pJ, float add 23 pJ, 8-lane FMA 28 pJ on zeros and 59 pJ on random data; a tensor multiply-add 0.4 pJ on zeros, 6 pJ on random |
| 3.1 | [Every instruction](03a-every-instruction.md) | all 161 instructions the silicon executes in U-mode, three shuffled passes on two cards: cheapest `fence` at 4.6 pJ, dearest `amoaddg.d` at 1486 pJ; pass-to-pass standard error 1.9% in the median; the second card at 0.950× over all 386 configurations |
| 4 | [Bytes through memory](04-bytes-memory.md) | L1 hit 0.5 pJ/B, own scratchpad 2–8 pJ/B, DRAM 90–140 pJ/B; writes through the L1 to DRAM 250–350 pJ/B |
| 4.3 | [Finer grain: wires, lines, rows, leakage](04a-fine-grain.md) | one mesh hop costs 1.7 pJ/B on random data and 0.7 on zeros, so toggling a bit across one hop is 131 fJ [129–133]; filling a 64 B line into the L1 is 110–210 pJ; the DRAM row pattern does not change the energy; the SRAM leaks 1.6 W at 67 °C and 2.6 W at 82 °C; where each class's current flows, by rail; the unmetered remainder attributed (18–20% delivery loss on the minion rail, 70 pJ per DRAM byte off-rail) and a droop meter for DRAM |
| 5 | [Bytes between cores](05-bytes-between-cores.md) | under 1 pJ/B in a neighbourhood, 2 in a shire, 12–18 across the mesh; 8.6 pJ/B to hand a slab to the next shire, a twelfth of the DRAM round trip |
| 6 | [Synchronisation](06-synchronisation.md) | a contended atomic 20 nJ [17–24]; a spread one 1.2 nJ; a chip barrier is 5,000 cycles of leakage |
| 7 | [Composition](07-composition.md) | a dense matmul at 80 °C is 57% static energy; the relay is predicted from §4 within 10% |
| 8 | [Card-to-card variation](08-cards.md) | the second card is 0.95× the first, in every table |
| 9 | [Method and limits](09-method.md) | how each number was made, how the bars were made (three passes on two cards; warm die; bursts that moved the clock or starved the sampler dropped), and what it cannot tell you |

Everything is at **600 MHz and 0.517 V**, the point the governor pins a warm card to, unless stated.

## Regenerating

```
python3 tools/ettelem/build_energy_manual.py --out docs/reports/data/2026-09-23-energy-manual/manual.json
python3 tools/ettelem/render_energy_manual.py docs/reports/data/2026-09-23-energy-manual/manual.json docs/energy-manual/
```

The first collects every table from its data file (the JSON records which); the second renders these pages
from that JSON, so a number here is never typed by hand. The instruction catalogue itself is
`workloads/enercat`: `run_enercat.sh` measures, `analyze_enercat.py` reduces.

Published: <https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual>. Provenance: `docs/findings/`.
