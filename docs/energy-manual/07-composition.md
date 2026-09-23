# 7. Composition: building a workload's energy from the tables

The equation from the structure page, applied. Three examples, each compared with a direct measurement.

## 7.1 A dense fp32 matmul: where the joules go

`TensorFMA32` on random data, all 1,024 minions, 7 seconds, launched at 80 °C (E9).

| Component | Source | W | J in 7 s | Share |
|---|---|---|---|---|
| Fixed (PCIe, DDR PHY, IO, regulators) | §1, $P_\text{fix}$ | 12.6 | 88 | 20% |
| Leakage at 80 °C | §1, $P_\text{leak}(80)$ | 23.3 | 163 | 37% |
| Tensor state machines, 1,024 minions | §3.2, 1.81 mW × 1,024 | 1.9 | 13 | 3% |
| Multiply-adds, 4.59e+12 per second at 6.02 pJ | §3.2 | 25.8 | 180 | 41% |
| **Predicted board power** | | **63.5** | 445 | |
| Measured (E9, `p80` of randn) | | 63.9 | | |

Per flop, that is **6.9 pJ loaded** and **3.0 pJ marginal**: 57% of the energy of the most arithmetic-dense thing this chip does is spent keeping the card on and leaking. The same matmul on zeros draws 1.9 W over idle instead of 27.6, and the loaded cost per flop becomes 4.1 pJ, almost all of it static. **On this card the data decides the dynamic energy, and the temperature decides the rest.**

## 7.2 The relay (E25), predicted from §4 alone

The multi-stage relay was measured on 22 September and no table in this manual was fitted to it. Its data is one constant per slab, so the prediction is bracketed by the zeros and random rows; the read side of the hop uses the 18 September remote-scratchpad read.

| Medium | Predicted pJ per byte moved (zeros … random) | Measured | Inside the bracket |
|---|---|---|---|
| DRAM round trip | 90 … 137 | 104.8 | yes |
| Own scratchpad | 3.2 … 6.1 | 4.25 | yes |
| Next shire's scratchpad | 5.3 … 7.1 | 8.89 | yes (a little above: the barrier and the add) |

Each byte in the relay is either read or written once, so the prediction is the mean of the read and write rows. The hop lands a little above its bracket because the relay also runs a vector add per element and a chip barrier per stage, neither of which §4 counts.

## 7.3 A hot line (E23), from §2 alone

1,024 minions stalled on one contended atomic: §2 says a stalled minion draws about 1.4 mW, so 1.43 W over idle. Measured: 1.41 W. Contention is not an energy problem; it is a throughput problem, and the energy it wastes is the leakage of the time it takes.

## The rule for a new workload

1. Time it, or predict its time from the roofline: the slowest of its instruction issue (§3 rates), its bytes (§4, §5 rates) and its synchronisation (§6).
2. Static energy is that time times $P_\text{idle}(T)$ from §1, at the temperature the card will actually be at — which the workload sets (docs/findings/12-heat-management.md).
3. Add $N_i e_i$ for each row it touches, choosing the zeros / constant / random column by what its data looks like.
4. Expect the answer within about 10%, and within 5% of the same on aifoundry3 (§8).
