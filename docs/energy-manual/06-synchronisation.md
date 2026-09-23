# 6. Synchronisation

Every entry is **mean** [lo–hi]: the mean over every pass on every card, and the full range those passes spanned. "a2" and "a3" are aifoundry2 and aifoundry3, each as its own mean ± its pass-to-pass standard error. The hot line was measured on 22 September and re-run three times on each card on 23 September (n = 7).

| Event | Energy | per card | Time | Note |
|---|---|---|---|---|
| Global atomic, one line, 1,024 requesters | **19.8** [16.9–23.6] nJ | a2: 20.8 ± 1.0 · a3: 18.6 ± 1.1 | 10 cycles each at the bank | the bank serialises; every requester stalls |
| Global atomic, 32 lines, one per shire | **1.2** [1.0–1.4] nJ | a2: 1.2 ± 0.1 · a3: 1.1 ± 0.1 | 0.31 cycles each, aggregate | the same instruction, 17× cheaper |
| Uncontended remote atomic round trip | — | | 216 cycles | E22 |
| Chip-wide barrier, 1,024 minions | ≈ 11,939 nJ of waiting | | 4,997 cycles | derived: 1,024 minions stalled at 1.4 mW for the barrier's length; the 32 atomics and 32 credit stores are negligible beside it |
| FLB + credit barrier, one shire | — | | 237 cycles | nocbench, 18 September |
| TensorReduce + broadcast, 32 minions | — | | 432 cycles | nocbench, 18 September |

**What the table says.** A contended hot line is the single most expensive thing a program can do per operation on this chip, and its cost is not on the requesters: the shire that hosts the line loses its own memory path entirely (docs/findings/17-hot-line.md). Waiting itself is cheap — a stalled minion draws what a spinning one does, about 1.4 mW — so a barrier's energy is small next to the leakage the card burns while it lasts.

The contended row's bar is wide for the same reason as the awake table's: the whole chip stalled draws only 1.4 W over idle, and the per-operation figure divides that small number by a rate the bank fixes at one per 10 cycles.

Source: `docs/reports/data/2026-09-22-hotline-aifoundry2/hotline.json`, `docs/reports/data/2026-09-23-energy-manual/reruns.json`.
