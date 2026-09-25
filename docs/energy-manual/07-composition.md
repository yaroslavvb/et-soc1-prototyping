# 7. Composition: building a workload's energy from the tables

The equation from the structure page, applied. Three examples, each set against a direct measurement. Only
the relay is an out-of-sample check; the other two are decompositions, and say so.

## 7.1 A dense fp32 matmul: where the joules go

`TensorFMA` on random fp32 data, all 1,024 minions, 7 seconds, launched at 80 °C. The multiply-adds are priced
by the flip model of §3.2, not taken from the measurement, so the table is a decomposition checked against a
measurement, not a prediction: the flip model was fitted (E17) to this card's runs of the same patterns in E9
and E12, and the measurement is E15's, a later session on the same card.

| Component | Source | W | J in 7 s | Share |
|---|---|---|---|---|
| Fixed (PCIe, DDR PHY, IO, regulators at rest) | §1, $P_\text{fix}$ | 12.6 | 88 | 20% |
| Leakage at 80 °C | §1, $P_\text{leak}(80)$ | 23.3 | 163 | 37% |
| Tensor state machines, 1,024 minions | §3.2, 1.81 mW × 1,024 | 1.9 | 13 | 3% |
| Multiply-adds: the flip model's 27.2 W less the state machines | §3.2 | 25.3 | 177 | 40% |
| **Board power from the tables** | | **63.1** | 441 | |
| Measured (E15 ablation, fp32 random, at the 80 °C launch) | | 63.9 | | |

Per flop, that is **7.0 pJ loaded** (the measured 63.9 W over 9.18 TFLOP/s) and **2.89 pJ marginal**
[2.62–3.01 over runs and cards]: 57% of the energy of the most arithmetic-dense thing this chip does is spent
keeping the card on and leaking. The same matmul on zeros draws 1.9 W over idle instead of 27.6, and the loaded
cost per flop becomes 4.1 pJ, almost all of it static. **On this card the data decides the dynamic energy, and
the temperature decides the rest.**

## 7.2 The relay (E25), priced from §4

The multi-stage relay was measured on 22 September, and no row of §4 was derived from it, so this is an
out-of-sample check. It is a consistency check, not a prediction made before the measurement.

The relay reads with 32 B vector loads through the L1 and writes with tensor stores. Its "next shire" is shire
s − 1 by ID, which on the mesh is 3.5 hops away on average (1 to 10). Each byte is read once and written once,
so each bracket is the mean of the matching read and write rows, from zeros to random data, because the relay's
data is one constant per slab:

- own scratchpad: the 32 B loads through the L1 of §4.3 (stride 32) and the tensor store of §4.1;
- next shire: the wire read of §4.3 interpolated to 3.5 hops (a remote read over the mesh) and the same store;
- DRAM: the tensor load and tensor store of §4.1, the nearest rows the catalogue has.

| Medium | Priced pJ per byte moved (zeros … random) | Measured (E29: 22 September + reruns, n = 8) | Against the bracket |
|---|---|---|---|
| DRAM round trip | 90 … 133 | 105.7 [99.5–111.0] | inside |
| Own scratchpad | 4.3 … 7.1 | 3.99 [3.90–4.25] | 8% below |
| Next shire's scratchpad | 5.1 … 11.2 | 8.59 [7.78–9.21] | inside |

The relay also runs a vector add per element and a chip barrier per stage, and neither is in §4.

## 7.3 A hot line (E23): a consistency check

1,024 minions stalled on one contended atomic draw 1.41 W over idle on aifoundry2 (22 September). §2's figure of
1.4 mW per stalled minion is this same measurement divided by 1,024, so §2 cannot predict it; the row is here
to show the scale. Contention is not an energy problem; it is a throughput problem, and the energy it wastes is
the leakage of the time it takes.

## The rule for a new workload

1. Time it, or predict its time from the slowest of its instruction issue (§3 rates), its bytes (§4, §5 rates)
   and its synchronisation (§6).
2. Static energy is that time times $P_\text{idle}(T)$ from §1, at the temperature the card will actually be at —
   which the workload sets (docs/findings/12-heat-management.md).
3. Add $N_i e_i$ for each row it touches, choosing the zeros / constant / random column by what its data looks like.
4. Expect the answer to be about as good as the bars of the rows it uses, and expect aifoundry3 to read about 5%
   lower (§8).
