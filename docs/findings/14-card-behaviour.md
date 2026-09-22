# Finding: how this card behaves, and how to measure it without fooling yourself

**Sources:** E5, E6 (telemetry and rails), E9 (the protocol), E10 (the governor), E12 (long runs), R3 (the
firmware policy). Published as A3 and A4.

Everything here was learned by getting it wrong first. If you are about to measure power or temperature on an
ET-SoC-1, read this before designing the experiment.

---

## The clock governor is thermal first

The service processor runs a power-management task (`thermal_pwr_mgmt.c`, R3). While a kernel is running it
steps the minion operating point **down** if the die is above a software threshold (**65 °C**) *or* the
board's average power is above the TDP level (**65 W**), and **up** otherwise. The thermal branch is checked
first and wins.

This card's operating points, read from telemetry (E10):

| Point | Clock | Die voltage |
|---|---|---|
| lowest | 600 MHz | 516–518 mV |
| middle | 700 MHz | ~570 mV |
| highest | 800 MHz | 618–620 mV |

**Consequence:** a card that has been busy idles above 65 °C (72 °C on 09-20, 80 °C in the controlled runs) and
therefore runs *everything* at 600 MHz, whatever the power — which is why an earlier version of this work
concluded, wrongly, that "the clock never moves". It moves only from a cool die.

From a 62–63 °C die, after a night idle (E10):

| Workload | Seconds at 800 MHz (of ~7) | TFLOPS | Mean board W | Peak |
|---|---|---|---|---|
| zeros | 5.1 and 5.9 | **11.38, 11.81** | 36–38 | 39.5 |
| ones | 0.6–0.8 | 9.66, 9.73 | 40 | 56 |
| random normal | 0.1–0.3 | 9.29–9.33 | 55–56 | **87.8** |

So Horace He's speed effect (R8) does appear here — about **25%** for zeros against random data, where he
measured 15% on an A100 — but only while the die is below 65 °C. Above it, the same physics shows up as heat
instead of speed. Random data at 800 MHz touches 88 W for an instant before the governor pulls it back.

**When comparing anything, check `mhz.minion` in every sample**, and start runs well above 65 °C so the
governor cannot intervene.

## The telemetry, and what each number really is

`tools/ettelem` reads the management library directly (`libDM.so`), which exposes more than the stock CLI:

| Field | Meaning | Gotcha |
|---|---|---|
| `board_w` | board power, 10 mW steps | refreshed once per 133 ms service-processor pass; near-instantaneous otherwise |
| `sp.minion_w`, `sram_w`, `noc_w` | per-rail power | **~2 s moving averages**: they lag a step by about 2 s. Skip 2–3 s after any change before averaging |
| `temp_c.minshire[0]` | die temperature | **whole degrees**, and it is the *mean of 34 shire sensors*. Hot spots are hotter |
| `die_mv.*` | on-die voltage per rail | the minion rail droops ~1 mV under 18 W more load: the regulator senses at the die |
| `mhz.minion`, `mhz.noc`, `mhz.ddr` | clocks | the only reliable way to catch the governor |

- Six queries take about 22 ms, so 45 Hz is the practical ceiling; 10 Hz was used throughout.
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

Power at the same work rises ~0.65–0.8 W per °C, so **heat left over from one run contaminates the next**.
The protocol (E9):

1. Pre-heat with random-data bursts to 84 °C if the die is below it.
2. Idle until the sensor **first reads 80 °C** coming down — an edge, not a range.
3. Launch. Shuffle configurations into blocks so drift spreads evenly.
4. Burn in a few cycles first, so the heatsink reaches its periodic state.

Achieved: launch temperature **80.96 ± 0.11 °C** and idle power **36.29 ± 0.06 W** across 46 runs; repeats
agree to 0.03–0.08 W for most patterns.

Approach times were 12–120 s (median 63 s) for 7-second runs, and up to six minutes after a run that reached
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
| Clock ever above 600 MHz | yes, 700 and 800 | **no, ever** | — |
| Idle | 31–36 W at 73–80 °C | 23.6 W at 51 °C | — |

**aifoundry3 is pinned at 600 MHz, and the reason is a flashed zero.** The governor's step-down test is
`measured power > TDP` and its step-up test is `<`. At a TDP of zero the first is always true and the second
never is, so the loop throttles down every 10 ms and nothing can lift it. The card's own log says so:
`Power throttle down event, current pwr 35380  tdp level: 0`, 26 times in one 8 KB window, with no step-up
event at all. A second reading agrees: `get_power_state()` classifies a card as `MAX_POWER` exactly when power
exceeds the TDP, and aifoundry3 reports `max_power` while drawing 23 W.

**The driver will not warn you.** Its `ETSOC1_IOCTL_GET_DEVICE_CONFIGURATION` reports the nameplate 65 W on
all three machines, including aifoundry3. Any host-side check passes. The card works; it is simply capped for
life at the bottom of its VMIN table.

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
- **The environment is not stationary.** Mid-session the lab's airflow changed and the die fell 12 °C under
  constant power. Record enough telemetry to notice.
