# What the meters miss, what the bars say, and what would let the card show more

The measurement side of the energy manual, as of 23 September 2026. Published as the second edition of
[Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability), which is now
the hub for every measurement report on these cards (it carries the index), and as the third edition of the
[energy manual](https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual). Sources: E29, E30, R13.

## The meter chain

A PMIC on the board measures the 12 V input and, over PMBus, the three regulators that feed the minion cores,
the SRAM arrays and the mesh: for each, voltage, current and power on both sides, and temperature, as
current/min/max/average — 84 numbers the service processor reads every loop pass. It forwards the **output-side
power** of each as a first-order filtered average (τ ≈ 1 s) with min and max, and the input power; `ettelem`
samples them at 10 Hz. The other rails — DDR core 0.8 V, VDDQ 1.1 V, VDDQLP, PCIe logic, PCIe/PShire, IO shire,
Maxion — have set points in the PMIC and no telemetry. So one number for the card, three for its inside, and at
idle at 73 °C the difference is 15.1 W of 31.8 (47%).

## The unmetered remainder, attributed (E30)

Fitted over the catalogue's bursts as a fraction of each rail's watts plus a cost per DRAM byte, no intercept:

| unmetered W = | aifoundry2 | aifoundry3 |
|---|---|---|
| × minion-rail W | 0.196 ± 0.003 | 0.177 ± 0.002 |
| × SRAM-rail W | 0.050 ± 0.017 | 0.064 ± 0.014 |
| × NoC-rail W | 0.286 ± 0.021 | 0.264 ± 0.019 |
| per DRAM byte | 72.9 ± 1.6 pJ | 68.1 ± 1.4 pJ |
| residual rms | 0.35 W over 392 bursts | 0.30 W over 386 |

An instruction's unmetered energy is the minion regulator's delivery loss; a DRAM byte's is about 70 pJ in the
PHY, the I/O rail and the chips (a byte written through the L1 costs twice that, the line being read first);
the NoC coefficient is more than a regulator because the memory shires' logic, on an unmetered rail, works
whenever the mesh moves bytes to them. What stays inferred: the idle 12–15 W's split between DDR, PCIe, the
IO shire, Maxion and the regulators' own draw, and the DRAM term's split below its regulator.

## A droop meter for DRAM (E30)

The die's Moortec PVT subsystem (5 controllers; 35 live temperature sensors at 0.061 °C; 125 voltage-monitor
points at 14 bits; 40 process detectors, configured with measurement disabled; 2 external analog inputs with a
stub reader) measures no current. But the host already receives the memory shires' reading of the 0.8 V DDR
rail every 133 ms (`DM_CMD_GET_ASIC_VOLTAGE`, `ettelem`'s `die_mv.ddr`, 767 mV at idle against an
800 mV set point), and across 386 bursts it droops **0.84 mV per watt of off-rail DRAM power** (rms
0.36 mV; 0.025 mV per watt of anything else): 1 mV ≈ 1.2 W of DRAM at 10 Hz, calibrated
against the fit above, responding to DRAM traffic alone and not drifting with the die temperature. The minion
rail sags 0.068 mV per watt the cores draw, which the spatial temperature brief mapped shire by shire
from the SP's DEBUG trace; calibrated per shire that map is a spatial current meter for the metered rails.

## The bars (E29)

Every entry of the manual is now mean [lo–hi] over every pass on every card, with each card's mean ± se
beside it: the catalogue's 3 shuffled passes × 2 cards for instructions and bytes (±6% median, mostly the 5%
between cards); the relay (n = 8), the hot line (n = 7), the rings and the levels (n = 6) re-run
three times per card with the die held warm on aifoundry2. Relay through DRAM 105.7 [99.5–111.0] pJ/B,
next shire 8.6 [7.8–9.2]; contended atomic 19.8 [16.9–23.6] nJ; DRAM by plain loads
122 [117–129] pJ/B at 600 MHz on both cards.

Two instrument limits found on the way, both now handled by `tools/ettelem/analyze_reruns.py`:

- **The governor.** Below about 68 °C aifoundry2's clock goes to 700–800 MHz mid-burst; the first rerun
  session at 65 °C was contaminated in 5–25% of its samples and discarded. Passes are preheated to 76 °C and
  any burst whose samples show the clock off 600 MHz is dropped.
- **The meter starved by the workload.** Rings between shires s and s+16 slow the service processor's own
  management path (command latency 22 → 150 ms) and freeze the board reading for seconds; the burst reads
  45% low. Bursts are dropped by the sampler's own latency (`took_ms`), and that row is aifoundry3 only.

## The improvement ladder

Nineteen rungs in the observability report, ordered by cost: software on the data the card already gives
(bracketed bursts, the attribution, the droop meter, the latency check — done; deconvolving the rails' filter,
calibrating the per-shire IR-drop map into a current map — not yet), lab hardware without firmware (a PCIe
riser with shunts read at a kilohertz; an infrared camera over the open card; the second card — done),
firmware (forwarding the PMIC's input-side readings; exporting the 35 temperature sensors; enabling the process
detectors and the external analog inputs; faster unfiltered power; the ECC sources; a counter-select syscall —
all behind the signed-image caveat), and research (a cell library for the RTL; current sensing below the
regulators, which no shared card will get). The riser is the one that sharpens every small-signal bar; forwarding
the PMIC's input side is the one that measures the delivery losses instead of fitting them.
