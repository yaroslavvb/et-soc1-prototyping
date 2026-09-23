# 9. Method, and the limits of every table

## How a number in this manual was made

1. **Board power** is the PMIC's reading through the management interface, 10 mW resolution, refreshed every
   133 ms, sampled at 10 Hz by `tools/ettelem`. The three rail figures (minions, SRAM, mesh) are the service
   processor's own ~2 s moving averages and together account for about half of board power; the rest — PCIe,
   the DDR PHY, the IO shire, the regulators' own losses — has no sensor.
2. **Idle is subtracted locally.** Each measurement is a burst of a few seconds of back-to-back launches with
   six seconds of idle on either side; its idle is the mean of the two bracketing stretches, which removes the
   drift of idle power with die temperature to first order. The die still runs a little warmer during a burst
   than in the gaps, so the extra leakage — the §1 slope times the temperature difference — is taken out as
   well. Over the 23 September catalogue that correction was 0.71 W in the median and
   1.79 W at most, against signals of 1.3 to 26.6 W.
3. **Rates come from the device.** Every hart counts what it completed and the cycle counter says how long it
   took, at the 600 MHz the card is pinned to; wall-clock time would measure the host's launch overhead.
4. **Energy per event is power over idle times the burst's wall time, divided by the events completed in
   it.** The gaps between launches inside a burst draw idle power and cancel.

## What "per instruction" means

The cost of that instruction retired on every hart of every minion at once, above idle, including the
cost of the core being awake to issue it (§2, about 7 pJ per slot with both harts). The "marginal over the
`addi` loop" figures in the data subtract that, and go negative for a multi-cycle instruction that stalls
the core — the stall is cheaper than issuing `addi` every cycle — so they are given only where they mean
something.

## What a "flip" is, and is not

Only the tensor unit has been resolved below the instruction, and only because its RTL was available
(docs/findings/11-thermal-model.md). A register bit clocked, a net toggled: these are events in a simulation
of the design, counted for the operands the card ran, and the energies attached to them were fitted to the
card's power. They are **not** transistor switches — the open RTL has no cell library, no netlist and no
capacitances — and the fitted energy of one class absorbs whatever real switching correlates with it. The
scalar and vector units have no such model here; their tables are empirical, and the zeros / constant /
random columns are the only window on their data dependence.

## Uncertainty, table by table

| Table | Typical uncertainty | Why |
|---|---|---|
| §1 idle law | ±0.2 W from 64 to 88 °C; +0.7 W extrapolated to 50 °C on the other card | rms of the fit; E20 |
| §2, §3.1 instructions | ±3% | idle bracketing; two cards agree to 5% with a common scale |
| §3.2 tensor unit | ±2% at 80 °C | 46 strict runs, ±0.1 °C launch temperature |
| §4.1 bytes, 23 Sep | ±3–5% | the DRAM rows are the smallest signals over the biggest idle |
| §4.2 bytes, 18 Sep | ±10%, and **the clock was not pinned**: `implied_ghz` per row | the governor moved between 600 and 850 MHz that day |
| §5 rings | ± half the spread of two runs, shown | two independent sessions |
| §6 atomics | ±5% | one session, three launches per case |
| §7 predictions | within about 10% | the relay check |
| §8 card scale | 0.95 ± 0.03 | 56 entries |

## What is not in this manual

- **The other operating points.** Everything is at 600 MHz and 0.517 V. The V²f ratios in §1 say what to
  expect at 700 and 800 MHz (1.44× and 1.90× switching power) and one cool-start session agreed to within
  its noise, but no table was re-measured there.
- **Divide and square root**: they trap.
- **Per-flip energies outside the tensor unit.** See above.
- **Anything at the 0.4 V operating point Esperanto designed for.** This card's firmware does not offer it.
- **The unsensed 15 W.** It is the largest single component of idle and no instrument here can split it.
