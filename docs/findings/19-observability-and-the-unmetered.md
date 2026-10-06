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
every loop pass: with nothing polling about every 133 ms on aifoundry2, 135 ms on aifoundry1's card 1 and 224 ms on
aifoundry3, and 156, 158 and 263 ms while ettelem samples at 10 Hz (E41; why aifoundry3's pass is longer is not
established). It forwards the PMIC's own running average of each **output-side power** (roughly first-order: a
step reaches 55–57% after 1 s and 83–84% after 2 s, τ ≈ 1.15–1.22 s (superseded by E58: 1.01–1.10 s, one SP pass late; 0.54 s on aifoundry1's card 1's SRAM rail), measured over 242 and 229 bursts in
`catalogue.json` `rail_filter`; the SP does no filtering of its own) with its
min and max, and the input power; `ettelem` samples them at 10 Hz. The other rails — DDR core 0.8 V, VDDQ 1.1 V, VDDQLP, PCIe logic, PCIe/PShire, IO shire,
Maxion — have set points in the PMIC and no telemetry. So one number for the card, three for its inside, and at
idle at 73 °C the difference is 15.1 W of 31.8 (47%).

**What a meter of watts can price (the hub's §2 plane, added 5 October 2026).** Every event the reports priced was run
as fast as the card runs it, so its energy × that rate is the power it lifted the board by (for the flips and the
wires, the share a fit gives them inside a larger burst), and that power is all the meter sees. The hub's 45 events
span 8.9 decades of energy (25 aJ to 19.85 nJ) at lifts of 1.19–26.5 W; E48's 101 configurations span 6,232× at
3.12–26.2 W; sparse parity's solve, candidate and executed int8 multiply-add (E59) sit on one diagonal each, 11.4–14.5
W, and one minion's L1 gathers, timed to the cycle, would add about 5.6 mW (its energy per element borrowed from the
chip's run). What limits pricing is the baseline's σ ÷ the precision asked (3.33 W at 0.2 W and ±6%), 2.5–3.5 decades
above one reading's step (1 mW on a rail, 10 mW on the board). The band of a few watts is partly a selection: it is
where the chip's power lands when an event runs flat out, which is how every one was priced. The chart: "Every priced
event sits on a few watts: the energy-rate plane", a second view of "How many identical events before the meter sees
one?"; its points in `energy_events` and `energy_plane` of `limits-of-observability.data.json`, from
`tools/ettelem/sync_hub_data.py`. Numbers in 05-claims.md: "What the board's meter can price, event by event", E48
"Each configuration's lift" and E59 "A solve, a candidate and a multiply-add on one diagonal".

## The unmetered remainder, attributed (E30; three cards since E46)

Fitted over the catalogue's configurations (the mean of each configuration's passes) as a fraction of each rail's
watts plus a cost per DRAM byte, no intercept. Since 26 September the fit runs over E46's catalogue, three passes on
each of three cards, and these are the figures to quote (the hub's §4.2 table; `limits-of-observability.data.json`
`power.fit` and `power.checks.fit`, robust HC3 standard errors, written by `tools/ettelem/sync_hub_data.py` with
`fit_unmetered.py`):

| unmetered W = | aifoundry2 | aifoundry3 | aifoundry1-c1 |
|---|---|---|---|
| × minion-rail W | 0.188 ± 0.002 | 0.181 ± 0.002 | 0.102 ± 0.005 |
| × SRAM-rail W | 0.034 ± 0.012 | 0.043 ± 0.011 | 0.540 ± 0.020 |
| × NoC-rail W | 0.291 ± 0.016 | 0.294 ± 0.016 | 0.205 ± 0.025 |
| per DRAM byte | 72.7 ± 4.4 pJ | 72.7 ± 4.5 pJ | 81.6 ± 3.9 pJ |
| residual rms, configuration means | 0.33 W over 392 (1.0 W on the 17 DRAM configurations) | 0.31 W over 392 (1.0 W on the 17 DRAM configurations) | 0.48 W over 392 (1.2 W on the 17 DRAM configurations) |

aifoundry1's card 1 differs: its unmetered power follows the SRAM rail more than the minion rail, for a reason not
measured (it runs the older firmware and a higher SRAM-rail voltage). E30's fit of 23 September, over the two cards'
catalogue then, gave 0.196, 0.050, 0.286 and 72.9 pJ/B on aifoundry2 (rms 0.35 W over 392) and 0.177, 0.064, 0.264
and 68.1 pJ/B on aifoundry3 (0.30 W over 386); the text below was written from it.

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

So half of idle is on no rail sensor, as is between an eighth and a sixth of what an arithmetic workload adds
(median 16% of an instruction's watts on aifoundry2, 15% on aifoundry3 and 12% on aifoundry1's card 1, over E46's
catalogue; 17% and 15% over E30's) and about seven tenths of what DRAM traffic adds (70%, 73% and 72%; 69% and 65%
over E30's). The minion regulator's delivery loss comes out at 19%, 18% and 10% of what that rail delivers.

**On a workload the fit was not made on (E59, added 5 October 2026).** Sparse parity's energy runs on aifoundry3
(one run per size, 29 September) give the first held-out test, in joules per solve (the hub's §4.2 chart "One solve's
joules, as the card's meters report them"; `solve_energy` in `limits-of-observability.data.json`, from each run's
`energy.json` through `tools/ettelem/sync_hub_data.py`). Idle is 61–67% of a solve and 35–38% of a solve is on no
meter, almost all of it the off-rail half of the idle (12.9 W of a 23.7–23.9 W idle); of what a solve adds over idle,
the rails carry 95–97%. The fit puts 0.185, 0.680 and 3.147 J per solve on no meter over idle where the meters show
0.044, 0.256 and 1.409 J: 6.4–8.7% of the rails' joules, about the top of the rails' stated bias (−2% to +7%,
`workloads/sparseparity/tools/energy_reduce.py`), and the same in watts by the catalogue's method (0.38–1.13 W
measured against 1.19–1.63 W). So this workload cannot tell the fit's error from the meters'; the reducer's ±15% on
the part on no meter was checked where it was a quarter of what a solve adds, not 3–5%. Numbers in 05-claims.md, E59.

## A droop meter for DRAM (E30)

The die's Moortec PVT subsystem (5 controllers; 35 live temperature sensors at 0.061 °C; 125 voltage-monitor
points at 14 bits; 35 process detectors, configured with measurement disabled; 2 external analog inputs with a
stub reader) measures no current. But the host already receives the memory shires' reading of the 0.8 V DDR
rail every service-processor pass (`DM_CMD_GET_ASIC_VOLTAGE`, `ettelem`'s `die_mv.ddr`, 767 mV at idle against an
800 mV set point on aifoundry2 and aifoundry3, 764 on aifoundry1's card 1), and it droops in proportion to the
off-rail DRAM power of the fit above. Over E46's catalogue (392 configurations per card) the slope is **0.86, 0.87 and
1.00 mV per watt of off-rail DRAM power** on aifoundry2, aifoundry3 and aifoundry1's card 1 (rms 0.35, 0.37 and
0.26 mV; 0.034, 0.024 and 0.099 mV per watt of anything else): 1 mV ≈ 1.0–1.2 W of DRAM (the hub's §4.3,
`power.checks.droop`). E30's first calibration, on aifoundry2's 23 September catalogue, gave 0.87 mV/W over 386
configurations (rms 0.37 mV; 0.029 mV per watt of anything else). It responds
mostly to DRAM traffic, but not only: traffic with no DRAM access (mesh, scratchpad, L3 reads through the mesh)
droops it by up to about 2 mV (2.2 mV for the L3 reads), which it would read as up to about 2 W of DRAM. So it
separates DRAM from arithmetic in a mixed burst, but not from mesh traffic, and its idle reading moves by about 1 mV
between 71 and 77 °C. The minion rail sags 0.053, 0.061 and 0.028 mV per watt the cores draw on the three cards
(E46; 0.070 in E30, 0.137 on aifoundry3's own telemetry then). (E30's are the numbers `tools/ettelem/fit_unmetered.py`
wrote on 25 September; the inline fit first published said 0.84 mV/W and rms 0.36 mV.) The [Power and temperature](https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature) report (§3)
maps each shire's rails at idle from the SP's DEBUG trace; calibrated per shire, that map would be a spatial current
meter for the metered rails. The [spatial temperature brief](https://spacesheep.dev/@yaroslavvb/et-soc1-spatial-temperature-brief) covers what the
same sensors could do for temperature.

## The bars (E29; three cards since E43 and E46)

Every entry of the manual is mean [lo–hi] over every pass on every card, with each card's mean ± se beside it.
Since 26 September (the manual's §9): the catalogue is three shuffled passes on each of three cards (n = 9, E46); the
rings, the levels and the relay six passes on each card (n = 18, E43); the tensor rows four runs per card (n = 12,
E38); the hot line is still E29's (n = 7, aifoundry2 and aifoundry3). About half of a catalogue entry's bar is the
difference between the cards; pass-to-pass scatter on one card is 1–2% for most entries. Relay through DRAM
116.2 [104.5–135.3] pJ/B, next shire 8.9 [7.6–10.2]; contended atomic 19.8 [16.9–23.6] nJ; DRAM by plain loads
114.6 [89.0–141.3] pJ/B at 600 MHz (`manual.json` `.reruns`). The widest bars are the levels between L2 and the remote
scratchpad (±45–59% of the mean, half the range; the L2 and L3 rows move a lot from pass to pass) and the hot line (a
1.2 W signal on a drifting idle, ±17%); the DRAM relay is ±13%.

E29 (23 September, two cards, the die held warm on aifoundry2) had given the relay (n = 8) through DRAM 105.7
[99.5–111.0] pJ/B and next shire 8.6 [7.8–9.2], DRAM by plain loads 122 [117–129] pJ/B, the remote scratchpad ±16%, the
DRAM relay ±5.5% and the awake core ±5–7%, with the catalogue at ±6% median (mostly the 5% between the two cards).

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
