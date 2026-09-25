# 2. A core that is awake

The cost of a minion that is running and doing as little as it can: an `addi` loop, no memory, no data. Everything an instruction costs in section 3 is on top of section 1 and includes the awake core.

Every entry is **mean** [lo–hi]: the mean over every pass on every card, and the full range those passes spanned. "a2" and "a3" are aifoundry2 and aifoundry3, each as its own mean ± its pass-to-pass standard error.

| Configuration | pJ per instruction | per card | W over idle, 1,024 minions (a2) | Per minion (a2) | Rate |
|---|---|---|---|---|---|
| One hart per minion, `addi` loop | **5.5** [5.3–5.8] | a2: 5.8 ± 0.04 · a3: 5.3 ± 0.001 | 2.19 | 2.14 mW | 3.82 × 10¹¹/s |
| Both harts per minion | **7.2** [6.7–7.7] | a2: 7.4 ± 0.2 · a3: 6.9 ± 0.1 | 3.51 | 3.43 mW | 4.74 × 10¹¹/s |
| The second hart's share | 14.4 pJ per extra instruction | | 1.32 | 1.29 mW | |
| Ablation of 21 Sep: four adds and a branch per iteration, hart 0, 80 °C, 2 runs | 8.1 pJ | a2 only, run-to-run sd 0.02 W | 1.46 | 1.43 mW | 1.80 × 10¹¹/s |
| 1,024 minions stalled on one contended atomic (the hot line, E23; each waits about 10,000 cycles for its turn) | — | a2: 1.25 ± 0.06 · a3: 1.11 ± 0.06 W; both **1.19** [1.01–1.41] | 1.25 | 1.22 mW | — |
| For scale: every minion running a random-data fp32 matmul (the activity term, E15; 25.6 mW per minion with 256 or 512 active, 26.2 with 768) | — | a2 only | 27.63 | 27.0 mW | tensor state machines plus everything else that wakes |

**The addi loop is not the floor.** It increments seven registers, so its operands change on every instruction. With both harts a `nop` costs 5.3 pJ [4.7–5.9] and a `fence` 4.5 [4.3–4.8] per instruction ([3.1](03a-every-instruction.md)), so the awake core is about 4.5–5.3 pJ per issue slot. The ablation's loop issued at half the one-hart `addi` loop's rate, on hart 0 only; it is the loop behind the figures in [Why is the ET-SoC-1 low power?](https://spacesheep.dev/@yaroslavvb/et-soc1-why-low-power), 1.4 mW per minion and 8 pJ per instruction.

**Rules.** An awake minion costs about 2 mW; a second hart adds about 1 mW; a minion stalled on a contended atomic draws less than one spinning (1.2 against 2.1 mW). Keeping 1,024 minions awake for a second is 2–3.5 J, against 36 J for the card at 80 °C, so the awake cost is small next to leakage and next to real instructions.

The bars here are ±5–7%, about the catalogue's median, although the signal is small: 2–3 W over a 28–36 W idle that drifts by a few tenths of a watt with the die temperature. The two cards differ by 8% on the two-hart loop, which is the cross-card scale of section 8.

Sources: `docs/reports/data/2026-09-23-catalogue-aifoundry2/`, `-aifoundry3/`, `docs/reports/data/2026-09-21-horace-aifoundry2/ablation.json`.
