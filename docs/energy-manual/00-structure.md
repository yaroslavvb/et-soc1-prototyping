# The ET-SoC-1 energy manual: structure

**Purpose.** A catalogue of what every kind of operation on this card costs in joules, arranged so that the
energy of a whole workload can be built up from parts, and every number traceable to a measurement.

## The equation the manual is organised around

$$E(\text{workload}) \;=\; \int_0^{t} P_\text{static}(T(\tau))\,\mathrm{d}\tau \;+\; \sum_{i} N_i\, e_i$$

- $P_\text{static}(T) = P_\text{fixed} + P_\text{leak}(T)$: what the card draws doing nothing, which depends
  on die temperature and on nothing the workload does — except that the workload sets the temperature.
- $N_i$: how many events of kind $i$ the workload causes (instructions retired, bytes moved by path,
  register bits clocked, messages sent, barriers crossed).
- $e_i$: the energy of one such event at the operating point. Switching energy scales as $V^2$; the leakage
  term does not depend on activity at all.

The time $t$ is not free: it is set by whichever resource the workload saturates, so predicting energy means
predicting time too. Section 7 shows the roofline in joules.

## Hierarchy

| § | Level | What it catalogues | Status |
|---|---|---|---|
| 1 | **The card at rest** | $P_\text{fixed}$, $P_\text{leak}(T)$, the per-rail split of idle, the three operating points | measured (E17, E19, E10) |
| 2 | **A core that is awake** | the cost of a running minion doing nothing useful; of a stalled one; one hart vs two | measured (E15, E23), extended here |
| 3 | **Instructions** | scalar integer, scalar float, 8-lane vector float, vector integer, transcendental; tensor FMA per type; and the data dependence of each (zeros / constant / random operands) | tensor unit measured with an RTL flip model (E9–E17); **scalar and vector units measured here** |
| 4 | **Bytes through the memory hierarchy** | L1, L2, L2 scratchpad (own and remote), L3, DRAM; read and write; tensor load and store | reads measured (memhier E-2026-09-18); **writes measured here** |
| 5 | **Bytes between cores and shires** | TensorSend/Recv by distance, reduce and broadcast trees, scratchpad hand-off | measured (nocbench 2026-09-18, E25) |
| 6 | **Synchronisation** | barrier, credit, fast local barrier, global atomic (uncontended, contended) | measured (E22, E23), extended here |
| 7 | **Composition** | worked examples: dense matmul, the multi-stage relay, a hot line; predicted from the tables against measured | assembled here |
| 8 | **Card-to-card variation** | every table on aifoundry2 and aifoundry3; aifoundry1 is unavailable | measured here |
| 9 | **Method and limits** | telemetry resolution, idle subtraction and thermal drift, what a "flip" is and is not, uncertainty per table | written here |

## Units and conventions

- Energies are **above idle**: $e_i = (P - P_\text{idle}(T)) / \text{rate}$, with $P_\text{idle}$ taken from
  idle windows bracketing each measurement, at the same die temperature. Section 9 says how good that is.
- Per *event*, never per second: pJ per instruction, pJ per byte, fJ per register bit clocked, nJ per barrier.
- The operating point is stated for every table. Unless said otherwise it is **600 MHz at 0.517 V**, the point
  the governor pins a warm card to (docs/findings/16-dvfs-and-leakage.md).
- Where a number is data-dependent it is given three ways — zeros, constant, random — because on this chip the
  difference is large (docs/findings/10-data-dependent-power.md).
