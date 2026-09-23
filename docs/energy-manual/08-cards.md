# 8. Card-to-card variation

Every table in sections 2 to 6 was measured on aifoundry2 and repeated on aifoundry3 with the same binaries. aifoundry1 holds two cards that cannot be opened (docs/findings/14-card-behaviour.md).

| Comparison | aifoundry3 / aifoundry2 |
|---|---|
| Instruction and byte energies, 386 catalogue entries, 3 passes each | median **0.950**, 10th–90th percentile 0.906–0.987, range 0.75–1.08 |
| Relay, hot line, rings and levels, 24 entries | median 0.937, range 0.73–1.16 |
| Tensor-unit switching power, 8 operand patterns (E20) | 0.924 |
| Idle law extrapolated 25 °C below its fitted range (E20) | +0.73 W of 25 W |
| Minion voltage at 600 MHz | 523 mV against 518 mV, which predicts 2% *more* |

**What it says.** A second card of the same design gives the same energies to about 5%, with a single per-card scale factor that the voltage does not explain and that leans the same way in every table. One random-data run calibrates it. The catalogue is a property of the design; the last 5% is the card.

**How the bars split.** For the catalogue's 392 entries the pass-to-pass scatter on one card is 1–2% (median standard error) and the card-to-card difference is 5%: the bar an entry carries is mostly the card, not the day. The small-signal entries — the awake core, the hot line, the DRAM relay — are the exception; there the idle baseline's drift is the bar.
