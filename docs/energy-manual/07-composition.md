# 7. Composition: building a workload's energy from the tables

The equation from the structure page, applied. Three examples, each set against a direct measurement. The
relay is a consistency check whose pricing rows were chosen after it was measured; the other two are
decompositions, and say so. The published page
(section 7.1, "Build a workload's energy") prices any mix of up to three rows at any die temperature, with the
same rows and the same idle law, and starts from the first example below.

## 7.1 A dense fp32 matmul: where the joules go

`TensorFMA` on random fp32 data, all 1,024 minions, 7 seconds, launched at 80 °C. The multiply-adds are priced
with §3.2's marginal energy per multiply-add, the mean over the version-3 ablation's runs on three cards (four on
each, 26 September), times the measured rate, so the table is a decomposition checked against a measurement, not a
prediction: the measurement (aifoundry2's four runs of that ablation) is part of that mean.

| Component | Source | W | J in 7 s | Share |
|---|---|---|---|---|
| Fixed (the idle law's constant at its best fit; 7–16 W over the e-foldings that fit as well) | §1, $P_\text{fix}$ | 12.6 | 88 | 20% |
| Leakage at 80 °C (best fit; 20–29 W over the same e-foldings) | §1, $P_\text{leak}(80)$ | 23.3 | 163 | 37% |
| Multiply-adds: 5.78 pJ [5.35–6.13] × 4.59 × 10¹² per second | §3.2 | 26.5 [24.5–28.2] | 186 | 43% |
| **Board power from the tables** | | **62.4** | 437 | |
| Measured (the version-3 ablation on aifoundry2, fp32 random, four runs at the 80 °C launch) | | 63.6 | 445 | |

The idle law is aifoundry2's, and only its total is pinned down (35.9 W at 80 °C); how it splits into fixed and
leakage depends on the law's shape (§1), which moves the first two rows but not their sum. The other cards idle
above it — by 1.0 W on aifoundry3 and 10.1 W on aifoundry1's card 1 in the version-3 idle cycles — and the published
page prices each card with its own law, the same form refitted to that card's cycles (37.3 W and 48.9 W at 80 °C).
Priced instead with the flip model of §3.2, fitted on aifoundry2 (27.2 W for the tile, 1.9 W of it the tensor state
machines), the board comes to 63.1 W. Per flop, the measurement is **6.9 pJ loaded** (63.6 W over 9.18 TFLOP/s) and
**2.89 pJ marginal** [2.67–3.07 over runs and cards]: 57% of the priced energy of the most arithmetic-dense thing
this chip does is spent keeping the card on and leaking, and at 80 °C the static power (35.9, 37.3 and 48.9 W on the
three cards) exceeds the dynamic power of every kernel measured in this manual, at most 27.8 W (this matmul, on
aifoundry1's card 1). The same matmul on zeros draws 1.9 W over idle instead of 27.2 on aifoundry2, and its measured
loaded cost per flop becomes 4.2 pJ, almost all of it static. **On every card the data decides the dynamic energy,
and the temperature decides the rest.**

## 7.2 The relay (E25), priced from §4

The multi-stage relay was first measured on 22 September and re-measured in the version-3 check (six passes on
each of three cards, 26 September); no row of §4 was derived from it, but the rows that price it were chosen after
it was measured, so this is a consistency check with wide brackets, not a prediction.

The relay reads with 32 B vector loads through the L1 and writes with tensor stores. Its "next shire" is shire
s − 1 by ID, which on the mesh is 3.5 hops away on average (1 to 10). Each byte is read once and written once,
so each bracket is the mean of the matching read and write rows, from zeros to random data, because the relay's
data is one constant per slab:

- own scratchpad: the 32 B loads through the L1 of §4.3 (stride 32) and the tensor store of §4.1;
- next shire: the wire read of §4.3 interpolated to 3.5 hops (a remote read over the mesh) and the same store;
- DRAM: the tensor load and tensor store of §4.1, the nearest rows the catalogue has.

| Medium | Priced pJ per byte moved (zeros … random) | Measured (V3-RL, six passes on each of three cards, n = 18) | Against the bracket |
|---|---|---|---|
| DRAM round trip | 95 … 137 | 116.2 [104.5–135.3] | inside |
| Own scratchpad | 4.5 … 7.4 | 4.34 [3.75–5.07] | at its low edge (5% below it, within the noise) |
| Next shire's scratchpad | 5.3 … 11.8 | 8.92 [7.63–10.18] | inside |

The relay also runs a vector add per element and a chip barrier per stage, and neither is in §4. The brackets
are wide: priced instead with the constant-operand rows of §4.1, closer to the relay's data, DRAM comes to
99.3 pJ/B on aifoundry2 against 111.3 measured, 95.9 on aifoundry3 against 107.5 and 117.2 on aifoundry1's card 1
against 129.9: the relay reads 10–12% above that price on every card.

## 7.3 A hot line (E23): a consistency check

1,024 minions stalled on one contended atomic draw 1.19 W over idle [1.01–1.41], pooled over seven passes on the
two cards (the first session, on aifoundry2 on 22 September, gave 1.41 W). §2's figure of 1.2 mW per stalled
minion is this same measurement divided by 1,024, so §2 cannot predict it; the row is here to show the scale. Contention is not an energy problem; it is a throughput problem, and the energy it wastes is
the leakage of the time it takes.

## The rule for a new workload

1. Time it, or predict its time from the slowest of its instruction issue (§3 rates), its bytes (§4, §5 rates)
   and its synchronisation (§6).
2. Static energy is that time times $P_\text{idle}(T)$ from §1, at the temperature the card will actually be at —
   which the workload sets (docs/findings/12-heat-management.md).
3. Add $N_i e_i$ for each row it touches, choosing the zeros / constant / random column by what its data looks like.
4. Expect the answer to be about as good as the bars of the rows it uses, and expect the cards to differ by a few
   per cent (§8): aifoundry3, at its own cooler die temperature, about 3% lower than aifoundry2; aifoundry1's card 1
   about 5% lower per instruction but 15% higher per byte, and its idle about 10 W higher (§1).
