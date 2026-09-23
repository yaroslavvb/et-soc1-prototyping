# 2. A core that is awake

The cost of a minion that is running and doing as little as it can: an `addi` loop, no memory, no data. Everything an instruction costs in section 3 is on top of section 1 and includes this.

Every entry is **mean** [lo–hi]: the mean over every pass on every card, and the full range those passes spanned. "a2" and "a3" are aifoundry2 and aifoundry3, each as its own mean ± its pass-to-pass standard error.

| Configuration | pJ per instruction | per card | W over idle, 1,024 minions (a2) | Per minion | Rate |
|---|---|---|---|---|---|
| One hart per minion, `addi` loop | **5.5** [5.3–5.8] | a2: 5.8 ± 0.0 · a3: 5.3 ± 0.0 | 2.19 | 2.14 mW | 3.82e+11/s |
| Both harts per minion | **7.2** [6.7–7.7] | a2: 7.4 ± 0.2 · a3: 6.9 ± 0.1 | 3.51 | 3.43 mW | 4.74e+11/s |
| The second hart's share | 14.4 pJ per extra instruction | | 1.32 | 1.29 mW | |
| Ablation of 21 Sep, hart 0, 80 °C, 2 runs | 8.1 pJ | a2 only, run-to-run sd 0.02 W | 1.46 | 1.43 mW | 1.80e+11/s |
| 1,024 minions stalled in a load that never returns (hot line, E23) | — | | 1.41 | 1.4 mW | — |
| Activity term under a dense matmul (E15) | — | | 26.2 | 25.6 mW | tensor state machines plus everything else that wakes |

**Rules.** An awake minion costs about 2 mW; a second hart adds about 1 mW; a minion stalled on memory costs the same as one spinning. Keeping 1,024 minions awake for a second is 2–3 J, against 36 J for the card at 80 °C, so the awake cost is small next to leakage and next to real instructions.

The bars here are the widest in the manual in relative terms, because the signal is small: 2–3 W over a 28–36 W idle that drifts by a few tenths of a watt with the die temperature. The two cards differ by 8% on the two-hart loop, which is the cross-card scale of section 8.

Sources: `docs/reports/data/2026-09-23-catalogue-aifoundry2/`, `-aifoundry3/`, `docs/reports/data/2026-09-21-horace-aifoundry2/ablation.json`.
