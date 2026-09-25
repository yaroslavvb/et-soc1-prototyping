# 6. Synchronisation

Every entry is **mean** [lo–hi]: the mean over every pass on every card, and the full range those passes spanned. "a2" and "a3" are aifoundry2 and aifoundry3, each as its own mean ± its pass-to-pass standard error. The hot line was measured on 22 September on aifoundry2 and re-run on 23 September, three warm passes on aifoundry2 and three on aifoundry3 (n = 7); the first session alone gave 23.6 and 1.37 nJ.

| Event | Energy | per card | Time | Note |
|---|---|---|---|---|
| Global atomic, one line, 1,024 requesters | **19.8** [16.9–23.6] nJ | a2: 20.8 ± 1.0 · a3: 18.6 ± 1.1 | 10 cycles each at the bank | the bank serialises and every requester waits its turn; the host shire's own loads stop |
| Global atomic, 32 lines, one per shire | **1.16** [1.01–1.37] nJ | a2: 1.21 ± 0.08 · a3: 1.09 ± 0.05 | 0.31 cycles each, aggregate | the same instruction, 17× cheaper |
| Uncontended remote atomic round trip | — | | 216 cycles | E22 |
| Chip-wide barrier, 1,024 minions | ≈ 10 µJ of waiting | | 5,018 cycles | derived: 1,024 minions stalled at 1.2 mW (§2) for the barrier's length; the 32 atomics and 32 credit stores are negligible beside it |
| FLB (fast local barrier) + credit barrier, one shire | — | | 237 cycles | [On-chip communication](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication), 18 September |
| TensorReduce (the hardware reduction tree) + broadcast, 32 minions | — | | 432 cycles | [On-chip communication](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication), 18 September |

**What the table says.** A contended atomic costs 17× the same atomic spread over 32 lines, and its cost is not on the requesters: the shire that hosts the line keeps its share of the atomic, but its own other loads stop ([One hot line stops a shire](https://spacesheep.dev/@yaroslavvb/et-soc1-hot-line), docs/findings/17-hot-line.md). Waiting itself is cheap — a stalled minion draws about 1.2 mW, less than a spinning one (2.1 mW, section 2) — so a barrier's energy is small next to the leakage the card burns while it lasts.

The contended row's bar is wide because the whole chip stalled draws only about 1.2 W over idle (1.4 W in the first session), and the per-operation figure divides that small number by a rate the bank fixes at one per 10 cycles.

Source: `docs/reports/data/2026-09-22-hotline-aifoundry2/hotline.json`, `docs/reports/data/2026-09-23-energy-manual/reruns.json`.
