# 6. Synchronisation

| Event | Energy | Time | Note |
|---|---|---|---|
| Global atomic, one line, 1,024 requesters | **23.6 nJ** | 10 cycles each at the bank | the bank serialises; every requester stalls |
| Global atomic, 32 lines, one per shire | 1.4 nJ | 0.31 cycles each, aggregate | the same instruction, 17× cheaper |
| Uncontended remote atomic round trip | — | 216 cycles | E22 |
| Chip-wide barrier, 1,024 minions | ≈ 11939 nJ of waiting | 4,997 cycles | derived: 1,024 minions stalled at 1.4 mW for the barrier's length; the 32 atomics and 32 credit stores are negligible beside it |
| FLB + credit barrier, one shire | — | 237 cycles | nocbench, 18 September |
| TensorReduce + broadcast, 32 minions | — | 432 cycles | nocbench, 18 September |

**What the table says.** A contended hot line is the single most expensive thing a program can do per operation on this chip, and its cost is not on the requesters: the shire that hosts the line loses its own memory path entirely (docs/findings/17-hot-line.md). Waiting itself is cheap — a stalled minion draws what a spinning one does, about 1.4 mW — so a barrier's energy is small next to the leakage the card burns while it lasts.

Source: `docs/reports/data/2026-09-22-hotline-aifoundry2/hotline.json`.
