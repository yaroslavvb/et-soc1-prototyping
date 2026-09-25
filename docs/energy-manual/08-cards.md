# 8. Card-to-card variation

Every catalogue and rerun table in sections 2 to 6 was measured on aifoundry2 and repeated on aifoundry3 with the same binaries; the rows that ran on one card say so. aifoundry1 holds two cards that cannot be opened (docs/findings/14-card-behaviour.md).

| Comparison | aifoundry3 / aifoundry2 |
|---|---|
| Instruction and byte energies, 386 catalogue entries, 3 passes each, each card at its own die temperature (median under load 79 °C and 54 °C) | median **0.950**, 10th–90th percentile 0.906–0.987, range 0.75–1.08 |
| Relay, hot line, rings and levels, 24 entries | median 0.929, range 0.73–1.16; not one scale (the L1 level 0.79, the own-scratchpad level 1.10) |
| Tensor-unit switching power, 8 operand patterns (E20), launched at 81 °C and 56 °C | 0.924 |
| Idle law extrapolated 7–14 °C below its fitted range (E20) | +0.73 W of about 25 W; in the 23 September catalogue's idle stretches +0.61 W (aifoundry2 −0.23 W) |
| Minion voltage at 600 MHz | 523 mV against 518 mV, which predicts 2% *more* |

**What it says.** aifoundry3 reads about 5% lower than aifoundry2 (median 0.95; 10–90%: 0.91–0.99), each card at its own die temperature, aifoundry3's about 25 °C cooler. The voltage does not explain the scale; the die temperature has not been ruled out, so whether the last 5% is the card or its temperature is not yet known. Most tables lean the same way, but not all: the L1 and own-scratchpad levels of 4.2 differ from the scale beyond their noise, and no single catalogue entry differs from it beyond the noise of three passes once the 386 comparisons are allowed for.

**How the bars split.** For the catalogue's 386 shared entries the pass-to-pass scatter on one card is 1–2% (median standard error) and the card-to-card difference is 5%: about half of the bar an entry carries is the card, the rest the day. The smallest signal, the hot line (about 1.2 W over idle), carries one of the widest bars, ±17%, mostly because its first session read 1.4 W against 1.0–1.2 W in every pass since, and because on so small a signal the leakage correction, a few tenths of a watt, moves each pass by 10–25%; the awake core (±5–7%) and the DRAM relay (±5.5%) are about as wide as a typical catalogue entry.
