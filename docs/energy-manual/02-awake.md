# 2. A core that is awake

The cost of a minion that is running and doing as little as it can: an `addi` loop, no memory, no data. Everything an instruction costs in section 3 is on top of section 1 and includes this.

| Configuration | W over idle, 1,024 minions | Per minion | Per instruction | Rate |
|---|---|---|---|---|
| One hart per minion, `addi` loop | 2.03 | 1.98 mW | 5.6 pJ | 3.64e+11/s |
| Both harts per minion | 3.29 | 3.22 mW | 7.4 pJ | 4.49e+11/s |
| The second hart's share | 1.26 | 1.23 mW | 14.8 pJ per extra instruction | |
| Ablation of 21 Sep, hart 0, 80 °C | 1.46 | 1.43 mW | 8.1 pJ | 1.80e+11/s |
| 1,024 minions stalled in a load that never returns (hot line, E23) | 1.41 | 1.4 mW | — | — |
| Activity term under a dense matmul (E15) | 26.2 | 25.6 mW | — | tensor state machines plus everything else that wakes |

**Rules.** An awake minion costs about 2 mW; a second hart adds 1.2 mW; a minion stalled on memory costs the same as one spinning. Keeping 1,024 minions awake for a second is 2–3 J, against 36 J for the card at 80 °C, so the awake cost is small next to leakage and next to real instructions.

Sources: `docs/reports/data/2026-09-23-enercat-aifoundry2/`, `docs/reports/data/2026-09-21-horace-aifoundry2/ablation.json`.
