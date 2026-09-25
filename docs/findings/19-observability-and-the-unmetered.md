# What the meters miss, what the bars say, and what would let the card show more

[← Findings index](README.md) · published as [Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability) (A2,
second edition) and [the energy manual](https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual) (A15, third edition) · numbers and sources:
[05-claims.md](05-claims.md)

The measurement side of the energy manual, as of 25 September 2026. Limits of observability is now the hub for
every measurement report on these cards (it carries the index). Sources: E29–E32, R13. The
[PMIC](README.md#terms) is the board's power-management controller; the [service processor](README.md#terms) (SP)
is the on-die management core that reads it.

## The meter chain

A PMIC on the board measures the 12 V input and, over PMBus, the three regulators that feed the minion cores,
the SRAM arrays and the mesh: for each, voltage, current and power on both sides, and temperature, as
a current value, a minimum and maximum since reset, and a running average — 84 numbers the service processor reads
every loop pass, about every 133 ms on aifoundry2 (aifoundry3's readings change only about every 250 ms, for a reason
not established). It forwards the PMIC's own running average of each **output-side power** (roughly first-order: a
step reaches 55–57% after 1 s and 83–84% after 2 s, τ ≈ 1.15–1.22 s, measured over 242 and 229 bursts in
`catalogue.json` `rail_filter`; the SP does no filtering of its own) with its
min and max, and the input power; `ettelem` samples them at 10 Hz. The other rails — DDR core 0.8 V, VDDQ 1.1 V, VDDQLP, PCIe logic, PCIe/PShire, IO shire,
Maxion — have set points in the PMIC and no telemetry. So one number for the card, three for its inside, and at
idle at 73 °C the difference is 15.1 W of 31.8 (47%).

## The unmetered remainder, attributed (E30)

Fitted over the catalogue's configurations (the mean of each configuration's passes) as a fraction of each rail's
watts plus a cost per DRAM byte, no intercept:

| unmetered W = | aifoundry2 | aifoundry3 |
|---|---|---|
| × minion-rail W | 0.196 ± 0.003 | 0.177 ± 0.002 |
| × SRAM-rail W | 0.050 ± 0.017 | 0.064 ± 0.014 |
| × NoC-rail W | 0.286 ± 0.021 | 0.264 ± 0.019 |
| per DRAM byte | 72.9 ± 1.6 pJ | 68.1 ± 1.4 pJ |
| residual rms, configuration means | 0.35 W over 392 (1.1 W on the 17 DRAM configurations) | 0.30 W over 386 (1.3 W on the 11 DRAM configurations) |

An instruction's unmetered energy is the minion regulator's delivery loss; a DRAM byte's is about 70 pJ in the
PHY, the I/O rail and the chips (a byte written through the L1 costs twice that, the line being read first);
the NoC coefficient is more than a regulator because the memory shires' logic, on an unmetered rail, works
whenever the mesh moves bytes to them. The fit attributes what a workload adds above idle, not the idle itself.
What stays inferred: the idle 12–16 W's split (12–13 W on aifoundry3 at 51–56 °C, 14–16 W on aifoundry2 at
66–82 °C) between DDR, PCIe, the IO shire, Maxion and the regulators' own draw, and the DRAM term's split below its
regulator. The fit was first computed inline in the session; `tools/ettelem/fit_unmetered.py`, committed later,
reproduced its attribution exactly, and since 25 September it writes `unmetered_fit.json`, droop block included
(E30).

Two cautions. The DRAM residual is about a quarter of those configurations' unmetered power and has a pattern:
stores through the L1 sit 1.3–2.7 W above the fit because their line reads are not counted as bytes (counting them
lowers the DRAM rms to 0.76–0.80 W and the DRAM term to 70.2 and 65.8 pJ/B; the fit is kept as published), random
data sits above and zeros and constants below. And the 18–20% delivery loss holds only as far as the rails' meters
can be trusted: the rails are scaled by 1/0.94 for their filter, and each 1% of rail scale moves the minion
coefficient by about 1.2 points, which the fit cannot pin.

So half of idle is on no rail sensor, as is about a sixth of what an arithmetic workload adds (median 17% of an
instruction's watts on aifoundry2, 15% on aifoundry3) and three fifths to three quarters of what DRAM traffic adds
(median 69% and 65%; about 70% of a tensor load from DRAM).

## A droop meter for DRAM (E30)

The die's Moortec PVT subsystem (5 controllers; 35 live temperature sensors at 0.061 °C; 125 voltage-monitor
points at 14 bits; 35 process detectors, configured with measurement disabled; 2 external analog inputs with a
stub reader) measures no current. But the host already receives the memory shires' reading of the 0.8 V DDR
rail every 133 ms on aifoundry2 (`DM_CMD_GET_ASIC_VOLTAGE`, `ettelem`'s `die_mv.ddr`, 767 mV at idle against an
800 mV set point), and across 386 configurations it droops **0.87 mV per watt of off-rail DRAM power** (rms
0.37 mV; 0.029 mV per watt of anything else): 1 mV ≈ 1.2 W of DRAM, calibrated against the fit above. It responds
mostly to DRAM traffic, but not only: traffic with no DRAM access (mesh, scratchpad, L3 reads through the mesh)
droops it by up to about 2 mV (2.2 mV for the L3 reads), which it would read as up to about 2 W of DRAM. So it
separates DRAM from arithmetic in a mixed burst, but not from mesh traffic, and its idle reading moves by about 1 mV
between 71 and 77 °C. The minion rail sags 0.070 mV per watt the cores draw. (These are the numbers
`tools/ettelem/fit_unmetered.py` writes; the inline fit first published said 0.84 mV/W and rms 0.36 mV.) The [Power and temperature](https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature) report (§3)
maps each shire's rails at idle from the SP's DEBUG trace; calibrated per shire, that map would be a spatial current
meter for the metered rails. The [spatial temperature brief](https://spacesheep.dev/@yaroslavvb/et-soc1-spatial-temperature-brief) covers what the
same sensors could do for temperature.

## The bars (E29)

Every entry of the manual is now mean [lo–hi] over every pass on every card, with each card's mean ± se
beside it: the catalogue's 3 shuffled passes × 2 cards for instructions and bytes (±6% median, mostly the 5%
between cards); the relay (n = 8), the hot line (n = 7), the rings and the levels (n = 6) re-run
three times per card with the die held warm on aifoundry2. Relay through DRAM 105.7 [99.5–111.0] pJ/B,
next shire 8.6 [7.8–9.2]; contended atomic 19.8 [16.9–23.6] nJ; DRAM by plain loads
122 [117–129] pJ/B at 600 MHz on both cards. The widest bars are the smallest signals: the hot line (a 1.4 W
signal on a drifting 30 W idle) is ±17%, the remote scratchpad ±16%; the DRAM relay is ±5.5% and the awake core
±5–7%, no wider than the catalogue.

Two instrument limits found on the way, both now handled by `tools/ettelem/analyze_reruns.py`:

- **The governor.** Below about 68 °C aifoundry2's clock goes to 700–800 MHz mid-burst; the first rerun
  session at 65 °C was contaminated in 5–25% of its samples and discarded. Passes are preheated to 76 °C and
  any burst whose samples show the clock off 600 MHz is dropped.
- **The meter starved by the workload.** On aifoundry2, rings between shires s and s+16 slow the service processor's
  own management path (a telemetry sample of six management commands takes 76–146 ms instead of 22, the median in
  each of three passes; aifoundry3 stays at 22 ms), and the board value changes only 1.4–2.4 times a second against
  5–6 in the other rings (none held over 0.84 s); the burst's energy reads about 40% low (33–45% by pass). The
  reruns drop bursts by the sampler's own latency (`took_ms`, median over 60 ms), and that row is aifoundry3 only.
  DRAM reads slow the sampler too on aifoundry2: over a burst of tensor loads or row walks from DRAM, the median
  sample takes 23–206 ms and the longest 683 ms, while every aifoundry3 burst stays at 21–22 ms. The catalogue keeps
  those bursts and records each one's sampler latency: their board watts stand to aifoundry3's as every other
  configuration's do (aifoundry3 ÷ aifoundry2 0.94–0.99, against 0.91–0.99 for the middle 80% of the catalogue),
  though in the 3 of its 1,176 bursts on aifoundry2 that are over 60 ms the rails' readings are stale (the NoC rail
  up to 0.5 W below the same configuration's other passes), and dropping those 3 moves the E30 DRAM term from 72.9
  to 71.8 pJ/B, under one standard error.
  The heat-per-mm runs (E31, 2026-09-24) found a second case: on aifoundry2, tensor loads between shires in
  the same column three hops apart push a sample to about 1 s (1.6 s at worst). All six such bursts were
  dropped; aifoundry3 ran the same pairs at 22 ms.

Two more limits found on 2026-09-24, while making the heat-per-mm measurement (E31, E32):

- **The meter's queue can be poisoned.** A sampler killed in the middle of a request leaves its reply in the
  management queue; every later opener dies of `std::bad_function_call` on it and leaves its own, so a
  runner that simply retries never gets telemetry again. It stopped the first start of E32 on both cards.
  One `dev_mngt_service` call drains it, `ettelem sample` now exits cleanly on SIGTERM, and the runners
  drain and retry on a failed start ([14-card-behaviour.md](14-card-behaviour.md), "Traps").
- **A stray write is invisible.** Tensor stores from shire 0 to physical address 0 (the PU region's Maxion
  window), about a second in all, moved no error counter, no telemetry field and no clock. Nothing on the host
  would have noticed; the kernel's author did, from the code. The guard is in the tool, not the card.

## The improvement ladder

Twenty rungs in the observability report ([the ladder](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#improve)), ordered by cost:

| Group | Rungs | Status |
|---|---|---|
| Software on the card's own data | bracketed bursts (1), the attribution (2), the droop meter (3), sub-degree temperature by step timing (6), meter latency and queue checks (7) | done |
| Software, not yet | deconvolving the rails' filter (4), calibrating the per-shire voltage map into current (5) | tooling |
| Lab hardware, no firmware | a PCIe riser with shunts read at a kilohertz (8), an infrared camera over the open card (9), a second card (10) | tooling; 10 done |
| Firmware | forwarding the PMIC's input-side readings (11), exporting the 35 temperature sensors (12), the process detectors and analog inputs (13), faster unfiltered power (14), the ECC sources (15), a counter-select syscall (16) | needs a signed image |
| Tooling against existing interfaces | a libDM client for the Minion Debug Interface (17), a Verilator flow for the whole core-et bench (18) | tooling |
| Research | a cell library for the RTL (19), current sensing below the regulators (20) | research (19); not on this silicon (20) |

The riser is the one that sharpens every small-signal bar; forwarding the PMIC's input side is the one that
measures the delivery losses instead of fitting them.

## Related

- [17-hot-line.md](17-hot-line.md) and [18-on-chip-relay.md](18-on-chip-relay.md): the two tables the reruns put
  bars on.
- [20-heat-per-mm.md](20-heat-per-mm.md): the second starved-meter case and the poisoned queue, found there.
- [14-card-behaviour.md](14-card-behaviour.md): the telemetry fields and the traps.
- [15-earlier-findings.md](15-earlier-findings.md): the first edition of the observability survey.
