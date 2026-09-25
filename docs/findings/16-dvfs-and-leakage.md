# Finding: the DVFS loop measures power instead of estimating it, and never switches leakage off

[← Findings index](README.md) · published as [The ET-SoC-1's DVFS loop, and the leakage it never switches
off](https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage) (A11) · numbers and sources: [05-claims.md](05-claims.md)

**Sources:** R9 (David Kanter's statements, private notes), R3 (firmware source at `353f20e`), R2 (open RTL at
`b38a1a3`), E10 (the governor in action), E18 (the wake-up probe), E19 (an idle check after about 20.6 hours with
no workload).

In a conversation on 20 September 2026, David Kanter (MLCommons) described how a mature chip regulates its own
power. The notes of that conversation are private (R9); what follows paraphrases his statements. Six of them are
checkable against this chip. Three hold, one is consistent with everything seen but was never tested where it could
fail, one is wrong for this part, and one is in the open design but tied off.

DVFS is dynamic voltage and frequency scaling: the firmware moving the clock and the voltage together. The terms for
the chip (minion, shire, service processor, PMIC) are in [README.md](README.md#terms).

| What he said (paraphrased) | Verdict | Evidence |
|---|---|---|
| A mature design runs a DVFS loop that steps V and f to stay inside an envelope | **Confirmed** | Three operating points: 600 MHz at 0.517 V, 700 at 0.568, 800 at 0.618. Voltage moved with frequency in all 36 observed transitions |
| The chip counts bus bits and execution-unit activity and computes its own power estimate, on millisecond timescales | **Not on this chip** | The loop reads a measured PMIC wattage and a PVT temperature. No activity counter appears anywhere in it. He hedged that this might not hold for Esperanto's part; the hedge was right |
| Thermal sensors are in the same loop, because leakage depends on temperature | **Confirmed, and thermal wins** | The temperature test runs before the power test; 7 of 18 down-steps were thermal-only |
| Cache arrays sit behind leakage-suppression transistors, un-suppressed on demand at a small wake-up latency | **Tied off in the open RTL** | Per-minion sleep and isolation exist in the open (Erbium) RTL, tied off in that configuration, driven by no firmware line, and no wake-up latency is measurable. Whether the taped-out chip could gate its arrays is not established |
| Leakage is typically 5–30% of a design's power, ~20% common | **This card is worse** | 36% of a busy card, 65% of an idle one at 80 °C |
| Leakage costs power, not correctness | **Consistent, weakly tested** | Every result checked in this work was correct: the matmul benchmark checks its outputs bit-exact against a host reference and the relay checks every element. The power sessions' launches were not compared with a reference (no launch raised the tensor unit's error flag). The 20.6-hour idle is no evidence either way: nothing computed, DRAM ECC is compiled off and the SRAM ECC interrupt sources are never enabled ([15](15-earlier-findings.md)) |

---

## The loop, as the firmware builds it

The whole governor is `check_power_throttle_conditions()` in
`ServiceProcessorBL2/services/thermal_pwr_mgmt.c`, called once per pass of the device-management task, about
every 133 ms on aifoundry2 (each I2C sensor read waits 1 ms, then the pass sleeps `DM_TASK_DELAY_MS` = 10 ms). This is the source
at `353f20e`; the cards' own trace strings match an older build (see "Not established"):

```
T = pvt_get_minion_avg_temperature()      # on-die thermal sensor
P = pmic_read_average_soc_power()         # MEASURED board power, from the PMIC over I2C
if active_power_management and master minion is BUSY:
    if T > 65 °C:
        if f > f_min:  step DOWN one VMIN-LUT point   # at the floor: hold; the power tests are not reached
    elif P > 65 W and f > f_min:  step DOWN one VMIN-LUT point
    elif P < 65 W and f < f_max:  step UP   one VMIN-LUT point
on master minion going IDLE:  set frequency back to the boot point
```

Four consequences, all of which show up in the measurements:

- **The input is a measurement.** Nothing counts activity. Kanter's *P = C × V² × f* is never evaluated by
  this firmware, because the chip does not have to infer power — it has a meter.
- **Thermal has priority.** The temperature test comes first and the frequency check sits inside it, so above 65 °C
  the power tests are never reached, not even at the lowest operating point, where the thermal test itself does
  nothing. aifoundry2 usually rests above 65 °C (73 °C on 22 September, even after 20.6 hours with no work), so a
  kernel launched on it starts above the threshold and runs at the lowest operating point however little power it
  draws: all 1,112 launches of the strict protocol (E9, pre-heat and burn-in included) ran at 600 MHz. (An idle card sits at the boot point
  whatever its temperature, so idle readings are no evidence either way.) This is why the earlier work saw a card
  that "never changes clock". The test is `> 65` on a
  whole-degree reading, and E29 saw the clock lift to 700–800 MHz mid-burst below about 68 °C, so a measurement
  that must stay at 600 MHz preheats to about 76 °C.
- **There is no hysteresis.** `UPPER_POWER_THRESHOLD_GUARDBAND` and `LOWER_POWER_THRESHOLD_GUARDBAND`, a ±5%
  dead band, are **defined in the `353f20e` source and never used**. The older governor the cards' logs point to
  uses one of them, the upper; the thermal test has no dead band in either.
- **The clock returns to the boot point when the master minion reports idle**
  (`go_to_idle_state_and_update_pwr_status()`). Back-to-back launches rarely trigger it: the zeros runs held
  800 MHz across twelve and thirteen consecutive 0.37 s launches with 1–2 ms gaps.

## The loop, as the card runs it

The governor only moves when the die starts below 65 °C, so the evidence is the seven cool-start runs of
21 September (E10), which contain 36 clock transitions.

**It hunts, and the missing hysteresis explains it.** In one run of ones from a 64 °C die (charted in A11) the
board never came near 65 W (it peaked at 56 W); what the loop kept crossing was the 65 °C line. At a reading of 66 °C the clock
steps down; once the whole-degree reading is back at 65 °C the thermal test no longer fires, the power test sees
38 W < 65 W, and the clock steps back up. The clock changed seven times in 2.4 s, reaching 800 MHz twice, 1.6 s
apart. Then, with the die settled at 66 °C, it stayed at 600 MHz for the last 4.5 s. Over the whole 7.4 s run it
spent 5.6 s at the bottom point, 1.0 s at 700 MHz and 0.8 s at 800 MHz.

**Most down-steps can be attributed**, and the mix is informative:

| Cause | Count | Signature |
|---|---|---|
| Thermal only | 7 | die above 65 °C while the board drew 45–56 W, well under the limit |
| Thermal and power together | 4 | random data at 800 MHz, up to 88 W |
| Unattributed (reading ≤65 °C) | 7 | die 65 °C (once 64), board 34–56 W, so neither test fired on the values sampled. One (run 1, zeros, at 5.95 s: 800→600 MHz in a single step) looks like the boot-point reset; the other six are single-point steps in pairs 0.4–0.5 s apart, most likely thermal steps on passes where the service processor read 66 °C between our 10 Hz samples. Launches run back to back every 0.37–0.49 s, so every step is near a kernel boundary, which explains nothing |
| Power branch acting alone | **0** | on this card only random data at 700–800 MHz exceeds 65 W, and it takes the die through 65 °C within half a second |

**It is slow to start.** The first clock change came 0.39–0.99 s after a kernel launched: three to seven passes of
aifoundry2's ~133 ms loop. Once moving, it stepped on successive passes; eight up-steps go straight from 600 to 800 MHz
between two 100 ms samples, faster than one table point per pass. The `353f20e` source does not explain that; the
older governor the cards' logs point to climbs to the top point in one go.

## Leakage suppression: present, tied off, undetectable

**The design has the ports.** The open RTL of the neighbourhood (core-et's Erbium branch at `b38a1a3`: the same
Minion core lineage in a later MCU-class configuration, not the taped-out ET-SoC-1) carries a per-minion sleep
control and its acknowledge (`pwr_ctrl_min_nsleepin` / `nsleepout`, one bit per minion), a global pair, per-minion
isolation (`pwr_ctrl_min_isolate`), level shifters and a power stub that forces outputs safe while a domain is down —
a textbook power-gating structure at exactly the granularity Kanter described. That configuration has one
neighbourhood and no shire cache, so it says nothing about the L2/L3 arrays; for those, the wake-up probe below is the
only evidence.

**Nothing drives it.** In the open configuration the whole interface is tied off, with a comment saying so:

```verilog
// Power Ctrl - power control handled outside cpu subsystem and this ifce is not used
.pwr_ctrl_glb_nsleepin ('1),   // '1 = never asleep
.pwr_ctrl_min_nsleepin ('1),
.pwr_ctrl_min_isolate  ('0),
```

The service-processor firmware, searched at `353f20e`, contains no power-gating control of any kind. The only `PWR_CTRL` matches in the tree are an eMMC controller's bus voltage.

**And the card shows no sign of it (E18).** If an array were suppressed once idle, the first access afterwards
would pay the wake-up. The probe placed one line at a chosen level, spun the minion on its cycle counter for a
swept interval from zero to 27 ms (0, 1.7 µs, 17 µs … 27 ms) without touching that line, then timed a single load —
same line, only the idle time varying, 20 repeats:

| Level | Longest idle minus shortest |
|---|---|
| L1 | **0 cycles** |
| L1 after an evict to L1 | **0 cycles** |
| L2 | −11 cycles: a slow no-idle baseline (61 → 49.5 cycles), not the idle. With no idle at all the load reads 61 cycles, probably because the line was still settling after the asynchronous evict that placed it; at every idle from 1.7 µs to 27 ms it is a normal 49.5-cycle L2 hit |
| L3 | **0 cycles** |
| DRAM | +10.5 cycles (median of the paired differences; at 27 ms, 13 of the 20 are +9 to +14 cycles, six within 6 cycles of zero and one an outlier, −51): the row closing, an 11-cycle activate (tRCD), as the memory-anatomy report measured; present in full after 1.7 µs of idle and flat out to 27 ms, which is not how a wake-up would behave |

So on this card, in this firmware, no leakage suppression is in use; whether the taped-out chip could gate its arrays
is not established. The gating that demonstrably works is **clock** gating, which the open RTL uses aggressively
(per lane, per functional unit, with a seven-cycle tail). That is why an idle-but-powered core costs almost no
dynamic power and still leaks.

## What it costs, and a free validation

After **about 20.6 hours** with no workload (E19: since E16's last launch ended at 15:06 on 21 September, apart from
E18's 4.9-second probe five minutes before the sample), in a warmer room than the day before:

| | |
|---|---|
| Board power | **31.79 ± 0.04 W** at 73.0 °C |
| Minion rail | 11.05 W — a thousand cores doing nothing |
| SRAM rail | 2.00 W |
| Mesh rail | 3.64 W |
| On no rail sensor | 15.10 W (DDR, PCIe, regulator conversion) |
| Leakage model fitted 21 September | predicts **31.78 W** |
| Error | **+0.01 W** |

A different day, a different ambient, twenty hours of idling: the curve `12.6 W + 23.3 W · e^((T−80)/36)`
from [11-thermal-model.md](11-thermal-model.md) lands within 0.01 W. It is also evidence against any deep
idle state — after twenty hours the card sits exactly where the temperature curve says it should.

Leakage is **36% of a 64 W random-data matmul and 65% of an idle card at 80 °C** (23.3 of the idle law's 35.9 W;
`dvfs.json` `leak_fraction.idle_80c_law`): above Kanter's 5–30% whether
the card is busy or idle. Three things make it so, and only the third is the chip's own: (1) it runs at 0.52 V
rather than the 0.4 V Esperanto designed for; (2) a desktop chassis idles it at 73–80 °C rather than in server
airflow; (3) it carries 128 MB of shire SRAM (4 MB in each of 32 compute shires; Esperanto quotes over 160 MB on
die) with no array power gating in play.

## Consequences

- **The equation is right; it is just not what the loop uses.** Its activity term is strongly confirmed here:
  power over idle is close to linear in active minions (25.6 mW per minion at 256 and 512 active, 26.2 at 768 and
  27.0 at 1,024), and a model counting four classes of switching event predicts board power across fourteen
  operand patterns to 0.50 W rms, leaving one pattern out
  ([11-thermal-model.md](11-thermal-model.md)). The V²f term is only weakly testable, because the governor
  will not hold the high operating point long enough on a heavy workload.
- **Kanter's argument that measurement is expensive is weaker for this card, though it does not vanish.** His
  reason MLPerf cannot mandate measured power is that submitters will not pay to instrument a system. This chip is
  already instrumented as a load-bearing part of its own safety loop: a PMIC that meters the board, a service
  processor that reads it every pass, and a management interface that hands the number to the host. The cost of
  reporting the card's own power here is one query. MLPerf's measured power is the whole system (host, power supply,
  cooling), which this meter does not see, and the card's meter updates every 133 ms (on aifoundry2; about every
  250 ms on aifoundry3), with the rails behind the PMIC's running average (τ ≈ 1.2 s).
- **A provisioned-power metric cannot see the hunting.** Normalising by nameplate kilowatts scores a card by
  its rating, while on this card a badly damped governor moves real throughput by tens of percent inside a
  single 7-second run.
- **The hunting measured here is at the thermal threshold**, which has no dead band in either version of the
  source. The two power-guardband macros that `353f20e` leaves unused (the older governor uses one of them) would not
  damp it; damping it needs a temperature dead band.

## The second card answers the open question, and raises a new one

aifoundry3 runs the same firmware and never leaves 600 MHz, on a die 15 °C below the thermal threshold. Its
service processor reports a **static TDP of 0 W** where aifoundry2 reports 65 W (E21). In
`check_power_throttle_conditions()` the step-down test is `measured power > TDP` and the step-up test is `<`,
so at zero the first is a tautology and the second is unreachable. Each kernel start logs a power throttle-down
request and each kernel end an idle event: that 8 KB window of the card's trace buffer holds 26 throttle-down events
alternating with 27 idle events, and 0 throttle-up events, every one printing a TDP level of 0. (These lines are in the
older governor's format, which logs once per change of state; in the `353f20e` source the idle line prints no power,
and a throttle-down is logged only while the clock is above its minimum. See "Not established".) The clock
read 600 MHz in all 7,745 samples of the session.

**This establishes what the first version of the DVFS brief (A11) could not.** The power branch never fired on its
own on aifoundry2, because that card usually idles above 65 °C and the thermal test comes first, so that
version listed it as unverified. On aifoundry3 it is the only branch that ever fires, at every kernel start.

**And it shows the loop has no floor check.** The governor never asks whether its threshold is sane. A TDP of
zero is not rejected at init, not logged as a warning, and not visible to the host: the driver's
`ETSOC1_IOCTL_GET_DEVICE_CONFIGURATION` reports 65 W on all three machines. The card runs at the bottom of its
VMIN table (the firmware's table of operating points) for as long as its flashed TDP stays at zero, and the only
symptom is that it is slow.

## Not established

- Whether the taped-out ET-SoC-1 drives its sleep transistors under some other firmware or in some other power
  state. The chip-level netlist is not in the open drop; the RTL statement covers the Erbium configuration, and
  the card corroborates it only in the sense that nothing observable uses it.
- What the boot frequency is set to in flash.
- Why aifoundry3's flashed TDP is 0 W, and whether it was ever different. Traced to
  `g_pmic_power_reg.module_tdp_level`, no further.
- Whether the 8% switching-power difference between the two cards is silicon, package or board regulator.
- The wake-up probe can only detect a penalty larger than about ten cycles, for arrays idled up to 27 ms (the
  widest the delay op encodes). A gating policy with a longer timer would not show up.
- **Which firmware the cards run.** aifoundry3's service processor prints log lines that exist only in et-platform
  firmware before commit `60b40c10f` (24 September 2024, "Dvfs fixes and refactoring"), which reworked this governor; both cards report release
  1.3.1. In that older governor the power guardband is used, throttle events are logged once per state change, and
  a step-up climbs to the top point in one go. Everything above about the loop's code describes the `353f20e`
  source, not necessarily the governor on these cards.

## Related

- [11-thermal-model.md](11-thermal-model.md): the leakage law this page re-checks after a day's idle.
- [14-card-behaviour.md](14-card-behaviour.md): the three machines side by side, and how to measure without the
  governor moving the clock.
- [13-why-low-power.md](13-why-low-power.md): the operating points against an A100, term by term.
- [03-experiments.md](03-experiments.md): E10, E18, E19, E21, and the note on E10 re-analysed.
