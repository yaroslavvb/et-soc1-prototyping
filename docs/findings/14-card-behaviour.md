# Finding: how this card behaves, and how to measure it without fooling yourself

[← Findings index](README.md) · no single published page; the pieces are in
[Power and temperature](https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature) (A3), [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) (A4)
and [The ET-SoC-1's DVFS loop](https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage) (A11) · numbers and sources: [05-claims.md](05-claims.md)

**Sources:** E5, E6 (telemetry and rails), E9 (the protocol), E10 (the governor), E12 (long runs), E20 and E21 (the
second card, the three machines), E27 and E29 (the rails' filter, the meter traps), R3 (the firmware policy).

Everything here was learned by getting it wrong first. If you are about to measure power or temperature on an
ET-SoC-1, read this before designing the experiment.

---

## The clock governor is thermal first

The [service processor](README.md#terms) runs a power-management task (`thermal_pwr_mgmt.c`, R3), once per
management pass of about 133 ms on aifoundry2 (aifoundry3's readings change only about every 250 ms). While a kernel is running it steps the minion operating point **down** if the
die's whole-degree reading is above a software threshold (**65 °C**) *or* the board's average power is above the
TDP level (**65 W**), and **up** otherwise. The thermal branch is checked first and wins. This is the firmware
source at `353f20e`; the cards' own trace strings match an older build (R3), so details may differ on the card.
[16-dvfs-and-leakage.md](16-dvfs-and-leakage.md) has the loop in detail.

This card's operating points, read from telemetry (E10):

| Point | Clock | Die voltage |
|---|---|---|
| lowest | 600 MHz | 516–518 mV |
| middle | 700 MHz | 568 mV |
| highest | 800 MHz | 618–620 mV |

**Consequence:** a card that has been busy usually idles above 65 °C (72–80 °C on 20–22 September; about 65 °C on
23 September, when the governor did intervene) and therefore runs *everything* at 600 MHz, whatever the power — which is why an earlier version of this work
concluded, wrongly, that "the clock never moves". It moves only from a cool die.

From a 62–63 °C die, after a night idle (E10):

| Workload | Seconds at 800 MHz (of ~7) | TFLOPS | Mean board W | Peak |
|---|---|---|---|---|
| zeros | 5.1 and 5.9 | **11.38, 11.81** | 36–38 | 39.5 |
| ones | 0.6–0.8 | 9.66, 9.73 | 40 | 56 |
| random normal | 0.1–0.3 | 9.29–9.33 | 55–56 | **87.8** (`vf.json`, `randn800_peak`) |

So Horace He's speed effect (R8) does appear here — about **25%** for zeros against random data, where he
measured 15% on an A100 — but only while the die is below 65 °C. Above it, the same physics shows up as heat
instead of speed. Random data at 800 MHz touches 88 W for an instant before the governor pulls it back.

**When comparing anything, check `mhz.minion` in every sample**, and preheat to about 76 °C: the firmware's test
is `> 65` on a whole-degree reading, and E29 saw the clock lift to 700–800 MHz mid-burst below about 68 °C
([19-observability-and-the-unmetered.md](19-observability-and-the-unmetered.md)).

## The telemetry, and what each number really is

`tools/ettelem` reads the management library directly (`libDM.so`), which exposes more than the stock CLI:

| Field | Meaning | Gotcha |
|---|---|---|
| `board_w` | board power, 10 mW steps | refreshed once per service-processor pass, about every 133 ms on aifoundry2; on aifoundry3 the value changes only about every 250 ms (why is not established); near-instantaneous otherwise |
| `sp.minion_w`, `sram_w`, `noc_w` | per-rail power | **the PMIC's running average, roughly first-order with τ ≈ 1.15–1.22 s**: a step reaches 55–57% after 1 s, 83–84% after 2 s and about 94% after 3 s (E27, `catalogue.json` `rail_filter`, both cards), copied by the SP each pass (on aifoundry3 the copy changes about every 250 ms); not a moving average. Skip 2–3 s after any change before averaging. `ettelem sample --reset-ms` resets the statistics on a schedule, but whether that turns the average into a window mean is untested |
| `temp_c.minshire[0]` | die temperature | **whole degrees**, and it is the *mean of 34 shire sensors*. Hot spots are hotter |
| `die_mv.*` | on-die voltage per rail | the minion rail droops ~1 mV under 18 W more load: the regulator senses at the die |
| `mhz.minion`, `mhz.noc`, `mhz.ddr` | clocks | the only reliable way to catch the governor |

- One sample is six management commands and takes about 22 ms, so 45 Hz is the practical ceiling; 10 Hz was used
  throughout.
- **aifoundry3's readings refresh more slowly.** Its board value changes about every 250 ms, not 133: the sparsity
  energy runs on it (`docs/reports/data/2026-09-18-sparsity-aifoundry3/energy-{a,b}/power.csv`) polled 9.1 times a
  second, but the reading changed 4.0 times a second (median gap between changes 255 and 258 ms), against 7.04 times a
  second (median gap 117 ms) in aifoundry2's matmul run (`docs/reports/data/2026-09-18-aifoundry2/power.csv`). The
  rail values in the ettelem logs show the same difference between the cards. A sample takes 22 ms on both cards, so
  the cause is on the card, its SP loop or its PMIC; which is not established.
- The management node is **single-opener**. A telemetry sampler excludes other management users for the whole
  session, so start it once and leave it running.
- The three rails do not cover the memory shires or DRAM. Board minus rails is ~15 W idle and ~21 W under load.
- Finer voltage exists: raising the SP log level to DEBUG and extracting the trace gives a **per-shire** on-die
  voltage map (E6). Restore the log level afterwards.

## The sensor reads whole degrees — use the step times

A run's temperature rise read straight off the sensor is only good to about half a degree, which is useless
for a 0.1 °C effect. The trick used throughout: **the times at which the reading steps from one degree to the
next are sharp**, so fit the one number (the heating power) that, put through the thermal network and rounded
the way the sensor rounds, reproduces that run's readings.

This recovers the rise to about 0.03 °C on repeated runs, and the recovered heating power agrees with the
electrical measurement to about 1 W. It cannot resolve workloads that never move the reading — for the three
coolest patterns it only bounds the rise below about half a degree.

Power needs none of this. It reads in 10 mW steps.

## The measurement protocol that made results repeatable

Power at the same work rises with die temperature — the idle law's slope is 0.65 W per °C at 80 °C, and on
aifoundry2 power drifted 0.81 W per °C within the hot 7 s runs (82–86 °C; aifoundry3's 7 runs at 57–61 °C scatter too
widely to pin its drift down) — so **heat left over from one run contaminates the next**.
The protocol (E9):

1. Pre-heat with random-data bursts to 84 °C if the die is below it.
2. Idle until the sensor **first reads 80 °C** coming down — an edge, not a range.
3. Launch. Shuffle configurations into blocks so drift spreads evenly.
4. Burn in a few cycles first, so the heatsink reaches its periodic state.

Achieved: launch temperature **80.96 ± 0.11 °C** and idle power **36.29 ± 0.06 W** across 46 runs; repeats
agree to 0.03–0.08 W for most patterns.

Approach times were 12–120 s (median 63 s) for 7-second runs, and up to seven minutes after a run that reached
90 °C. **Budget three to eight times more wall-clock than card time.**

## The three lab machines are not interchangeable

Before using a card for anything comparative, read its governor configuration. Two read-only commands:

```
tools/etcfg                                  # the driver's view: TDP, boot clock, shire mask, cache sizes
LD_LIBRARY_PATH=/opt/et/lib build/ettelem/ettelem config   # the firmware's view: TDP, threshold, power state
```

| | aifoundry2 | aifoundry3 | aifoundry1 |
|---|---|---|---|
| Cards | 1 | 1 | 2, **neither usable** |
| Firmware / PMIC | 1.3.1 / 1.5.0 | 1.3.1 / 1.5.0 | not readable |
| TDP the driver reports | 65 W | 65 W | 65 W |
| **TDP the firmware reports** | **65 W** | **0 W** | — |
| Clock ever above 600 MHz | yes, 700 and 800 | **never seen** (10 Hz telemetry) | — |
| Idle | 31–36 W at 73–80 °C | 23.6 W at 50 °C (25.1 W at 56 °C under the runs) | — |

**aifoundry3 is pinned at 600 MHz, and the reason is a flashed zero.** The governor's step-down test is
`measured power > TDP` and its step-up test is `<`. At a TDP of zero the first is always true and the second
never is, so the loop logs a throttle-down at every kernel start, and nothing can ever step it up. The card's own
log says so: `Power throttle down event, current pwr 35380  tdp level: 0`, 26 times in one 8 KB window, alternating
with idle events, with no step-up event at all. A second reading agrees: `get_power_state()` classifies a card as `MAX_POWER` exactly when power
exceeds the TDP, and aifoundry3 reports `max_power` while drawing 23 W.

**The driver will not warn you.** Its `ETSOC1_IOCTL_GET_DEVICE_CONFIGURATION` reports the nameplate 65 W on
all three machines, including aifoundry3. Any host-side check passes. The card works; it is simply held at
600 MHz, the bottom of its VMIN table (the firmware's table of operating points), for as long as its flashed TDP
stays at zero.

**aifoundry1's two cards cannot be opened.** Its kernel module is built from different sources than the other
two (`srcversion 1383B256EB24A0A53F04CC7` against `47D26A305A0428B29FB7FC4`) while carrying the same
`libDM.so`, and the library's compatibility check refuses: `Error unable to evaluate compatibility!`. Its
`dev_mngt_service` is inactive. **This was not fixed** — replacing a kernel driver on a shared machine is a
lab-admin decision — and `tools/etcfg` still works there, because it talks to the driver and not the library.

Neither aifoundry3's TDP nor aifoundry1's driver was changed. Both would alter what other people's runs
measure, silently, in the middle of their experiments.

## Comparing cards: use switching power, not watts

aifoundry3 idles 11 W below aifoundry2 and at a different temperature, so absolute board power tells you
nothing across cards. What compares cleanly is **switching power**: board power during a run minus the idle
power measured just before it, which cancels that card's leakage at that temperature. On that basis the two
cards agree to 8%, and one scale factor removes even that. See [11-thermal-model.md](11-thermal-model.md).

## Traps that cost time here

- **`sparsity_host --budget` defaults to 8 seconds** on silicon and silently stops a longer run. Raise it for
  anything past 8 s.
- **Never edit a runner script while it is running.** Bash reads the file as it executes; a mid-run edit
  aborted a four-hour session at the last step.
- **`hpmcounter3` reads 128 short** when its low 7 bits are 0–10 (E2). Correct it (`fixcyc()`); the firmware's
  four-reads workaround does not fix it. The `cycle` CSR traps in U-mode.
- **`fcvt.s.lu` traps** (cause 0x1e): no 64-bit integer-to-float conversion. Use 32-bit counters in
  floating-point loops.
- **`evict_va` is asynchronous.** Fence and wait a few hundred cycles before timing, and note the level codes
  name where the line is *left* (1 = L2, 2 = L3, 3 = memory).
- **The L1 data cache is not coherent** and writes back whole 64 B lines. Harts on different minions must not
  share a line.
- **Only hart 0 of a minion may issue tensor ops**, except `TensorLoadL2Scp`/`TensorWait`.
- **Never let a minion receive readies from two `TensorSend` partners at once** — one ready bit per minion, not
  per partner. On silicon this hangs the hart permanently and the card needs a power cycle; `sys_emu` does not
  catch it.
- **The environment is not stationary.** Mid-session the lab's airflow changed and the die fell 12 °C under an
  unchanged workload. Record enough telemetry to notice.
- **A sampler killed mid-request poisons the management queue** (both cards, 2026-09-24). The reply to its
  last command stays queued. The next process to open `/dev/et0_mgmt` dies of `std::bad_function_call` on
  that reply and leaves its own behind, so retrying never recovers. Drain it once with
  `/opt/et/bin/dev_mngt_service -m DM_CMD_GET_MODULE_POWER -n 0 -u 5000`, which crashes on the stale reply and
  clears it. `ettelem sample` now finishes its request and exits on SIGTERM, and the runners drain the queue
  when a start fails (`start_sampler` in `workloads/enercat/run_wire.py` and the `tools/ettelem/run_*_power.sh`
  scripts). Stop a sampler with a plain `kill`, never `kill -9`. The driver's error counters did not move.
- **The workload can starve the meter.** Rings between shires s and s+16 (E29) push a telemetry sample (six
  management commands) from 22 ms to 76–146 ms on aifoundry2 (the median in each of three passes; 22 ms on
  aifoundry3). On aifoundry2, tensor loads between shires in the same column three hops apart (E31) push it to
  about 1 s, and 1.6 s at worst, so a burst gets a handful of stale samples.
  aifoundry3 ran the same pairs at 22 ms. DRAM reads slow it too on aifoundry2 (a median of 23–206 ms per sample over
  a burst of tensor loads or row walks from DRAM, 683 ms at most; E27). Every ettelem sample carries
  `took_ms`: check it. The reruns and the wire runs drop a burst whose median is over 60 ms; the energy catalogue keeps
  its three such DRAM bursts (of 1,176 on aifoundry2), since dropping them moves nothing beyond one standard error,
  but their readings are stale: the board value changed only 3–6 times in each 3.2 s burst (19 times in the median
  burst), and the NoC rail read up to 0.5 W below the same configuration's other passes.
- **A memory pattern launched without a buffer writes to physical address 0**, the start of the PU region's
  Maxion window. On 2026-09-24 a new enercat store mode that was missing from the host's list of memory modes
  sent tensor stores from shire 0 there, in two test launches of about half a second each. Nothing reported
  it: no error counter moved, telemetry stayed normal, and the card held 600 MHz and ran a normal burst
  straight after. `enercat_host` now refuses to launch a memory pattern with no slice. Add every new mode to
  that list before running it on a card.

## Related

- [16-dvfs-and-leakage.md](16-dvfs-and-leakage.md): the governor in detail, and the second card's zero TDP.
- [19-observability-and-the-unmetered.md](19-observability-and-the-unmetered.md): what the meters miss, and the
  improvement ladder.
- [11-thermal-model.md](11-thermal-model.md): the thermal network and the step-time trick for the whole-degree
  sensor.
- [03-experiments.md](03-experiments.md): the standard protocol and every session's command.
