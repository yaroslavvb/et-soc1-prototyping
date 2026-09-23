# 8. Card-to-card variation

Every table in sections 2 to 4 was measured on aifoundry2 and repeated on aifoundry3 the same day, with the same binaries. aifoundry1 holds two cards that cannot be opened (docs/findings/14-card-behaviour.md).

| Comparison | aifoundry3 / aifoundry2 |
|---|---|
| Instruction and byte energies, 56 entries | median **0.949**, range 0.87–1.01 |
| Tensor-unit switching power, 8 operand patterns (E20) | 0.924 |
| Idle law extrapolated 25 °C below its fitted range (E20) | +0.73 W of 25 W |
| Minion voltage at 600 MHz | 523 mV against 518 mV, which predicts 2% *more* |

**What it says.** A second card of the same design gives the same energies to about 5%, with a single per-card scale factor that the voltage does not explain and that leans the same way in every table. One random-data run calibrates it. The catalogue is a property of the design; the last 5% is the card.
