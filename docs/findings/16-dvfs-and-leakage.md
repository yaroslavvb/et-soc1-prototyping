# Finding: the DVFS loop measures power instead of estimating it, and never switches leakage off

[← Findings index](README.md) · published as [The ET-SoC-1's DVFS loop, and the leakage it never switches
off](https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage) (A11) · numbers and sources: [05-claims.md](05-claims.md)

**Sources:** R9 (David Kanter's statements, private notes), R3 (firmware source at `353f20e`, and since 27 September
the cards' own builds, 0.20.0 and 0.18.0), R2 (open RTL at `b38a1a3`), E10 (the governor in action), E18 (the wake-up
probe), E19 (an idle check after about 20.6 hours with no workload), E41 and E44 (the three-card check's meter chain and
idle cycles), E51 (the DV2 development night of 28 September, development data, and its frozen validation on the same
card, 28–29 September).

**Updated 2026-09-28.** This file had fallen behind [the page](https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage)
(its state of 27 September): the leakage shares are ranges, the correctness row is withdrawn, the timings and resting
temperatures are the page's. The governor the cards run is not the `353f20e` source the loop section below describes:
[14-card-behaviour.md](14-card-behaviour.md), "The clock governor, by firmware build", has the cards' own build, and
the notes marked **0.20.0** below say where it changes an explanation here.

**Updated 2026-09-29.** DV2's frozen validation (E51: a replication on aifoundry2, 28 September 20:45 PDT to
29 September 16:57 PDT) is reduced. No dead band (TH3), launch and end latencies set by the Master Minion's heartbeat
(TH4) and a residency counter that adds whole episodes (TH8) survived; "an idle exit is followed at once by the idle
reset" (TH7) fell, once in 52. The owner's two questions stayed untested by the frozen rules: every step that fitted a
rule fitted the mean and none the hottest sensor, but 7 of 9 separating runs is short of the 80% the rule asks
(TH1); the perimeter held 800 MHz longer in each of 4 complete blocks, 1.16–1.52 times, where the test needs 6 (Q2). The
build itself (TH2) is untested too. The card idled at 71–76 °C for most of the 20 hours, so its heating sessions ran
only in an evening cool spell. The development notes below stand as development evidence, each with the validation's
count beside it.

In a conversation on 20 September 2026, David Kanter (MLCommons) described how a mature chip regulates its own
power. The notes of that conversation are private (R9); what follows paraphrases his statements. Six of them are
checkable against this chip. Two hold, one holds at idle but is not established under load, one is wrong for this
part, and one is in the open design but tied off. The sixth, that leakage costs power but not correctness, was
withdrawn: two relay launches returned wrong elements while the clock dropped inside them.

DVFS is dynamic voltage and frequency scaling: the firmware moving the clock and the voltage together. The terms for
the chip (minion, shire, service processor, PMIC) are in [README.md](README.md#terms).

| What he said (paraphrased) | Verdict | Evidence |
|---|---|---|
| A mature design runs a DVFS loop that steps V and f to stay inside an envelope | **Confirmed** (aifoundry2) | Three operating points: 600 MHz at 0.517 V, 700 at 0.568, 800 at 0.618. Voltage moved with frequency in all 36 transitions of the cool-start runs, and in all 275 clock changes of eight sessions on 21 and 23 September |
| The chip counts bus bits and execution-unit activity and computes its own power estimate, on millisecond timescales | **Not on this chip** | The loop reads a measured PMIC wattage and a PVT temperature. No activity counter appears anywhere in it. He hedged that this might not hold for Esperanto's part; the hedge was right |
| Thermal sensors are in the same loop, because leakage depends on temperature | **Confirmed, and thermal wins** | The temperature test runs before the power test; 7 of 18 down-steps were thermal-only |
| Cache arrays sit behind leakage-suppression transistors, un-suppressed on demand at a small wake-up latency | **Tied off in the open RTL** | Per-minion sleep and isolation exist in the open (Erbium) RTL, tied off in that configuration, driven by no firmware line, and no wake-up latency is measurable. Whether the taped-out chip could gate its arrays is not established |
| Leakage is typically 5–30% of a design's power, ~20% common | **Worse at idle; under load, not established** | On aifoundry2 at 80 °C the leakage is 20–29 W: 55–80% of an idle card and 31–45% of a 64 W random-data matmul (the best fit: 65% and 36%). The idle readings fix its slope, 0.65 W/°C, not its split from the fixed power, hence the ranges. The three-card check's cooling cycles allow 17–80% of a busy card, so above 30% under load is not established (E44, IDLE-k) |
| Leakage costs power, not correctness | **Withdrawn** (25 September) | This row used to say that every result checked in this work was correct. Two relay launches on aifoundry2 returned wrong elements (1,118 and 1,000) on 23 September, in one pass of the discarded first attempt at a cool-card rerun; both ran while the governor dropped the clock from 800 to 600 MHz inside the launch, and the relay's other launches on both cards were correct. An error at the clock transition and a race in the relay's completion flags when the clock ratio changes would both fit; one pass on one card cannot tell them apart. The page cut this verdict row on 27 September |

---

## The loop, as the firmware builds it

The whole governor is `check_power_throttle_conditions()` in
`ServiceProcessorBL2/services/thermal_pwr_mgmt.c`, called once per pass of the device-management task, about
every 133 ms on aifoundry2 (224 ms on aifoundry3, 135 ms on aifoundry1's card 1, with nothing polling; 160, 266 and
162 ms under a 10 Hz sampler: E41). Each I2C sensor read waits 1 ms, then the pass sleeps `DM_TASK_DELAY_MS`. This is
the source at `353f20e`; the cards run an older build (see the note after the four consequences):

```
T = pvt_get_minion_avg_temperature()      # integer mean of the 34 minion-shire sensors, each whole degrees
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
  whatever its temperature, so idle readings are no evidence either way.) Its rest is not fixed: 62–74 °C on the days
  before, 66–67 °C on 27 September, and on the night of 28 September it swung between 59 and 72 °C on a
  10–30 minute scale, for reasons not established (the host's ACPI zones read constant, probably not live; its drive
  read 43–47 °C and its CPU package 37–59 °C; E51, development); over DV2's 20 h validation (28–29 September) it read
  59–76 °C, 71–76 °C in 327 of 378 idle cycles and never below 65 °C after 23:18 PDT. This is why the earlier work saw a card
  that "never changes clock". The test is `> 65` on a
  whole-degree reading, and E29 saw the clock lift to 700–800 MHz mid-burst below about 68 °C, so a measurement
  that must stay at 600 MHz preheats to about 76 °C.
- **There is no hysteresis.** `UPPER_POWER_THRESHOLD_GUARDBAND` and `LOWER_POWER_THRESHOLD_GUARDBAND`, a ±5%
  dead band, are **defined in the `353f20e` source and never used**. The older governor the cards' logs point to
  uses one of them, the upper; the thermal test has no dead band in either.
- **The clock returns to the boot point when the master minion reports idle**
  (`go_to_idle_state_and_update_pwr_status()`). Back-to-back launches rarely trigger it: the zeros runs held
  800 MHz across twelve and thirteen consecutive 0.37 s launches with 1–2 ms gaps.

**0.20.0: what the cards' own build changes** (the source of release 1.3.1, et-platform `ffca4cbb4`; 14-card-behaviour.md
has it with its lines). The thermal test has no busy check, so it acts on an idle card too. Above 65 °C the service
processor enters a blocking loop: one point down, a 1,000-tick sleep (about 0.40 s), a fresh mean, repeated until the
mean reads 65 or less; while it runs the power branch, the idle reset included, cannot act. On exit the clock goes to
the boot point, and on the next pass a busy card under the TDP climbs to the top point in one call. The power test
compares the PMIC's instantaneous reading, not its average. The development night of E51 fits this build and not
`353f20e`: every thermal episode shorter than a minute lasted k × 0.4053 s to within 1.43 ms (17 of 17, k = 0–3; 16
on the idle card, 1 at a session start), 18 of the night's 20 thermal entries came after the SP's own idle line, all 57 climbs showed at most one
700 MHz sample, and aifoundry2's throttle residency put it in the thermal state for 8.65 of its 9.23 days of uptime
(development). Its frozen validation found most of it again (51 idle entries after the idle call or an exit, 67 of 67
one-call climbs) but left the build (TH2) untested: 44 of 46 idle loop intervals lay within 10.9 ms of the grid and the
two longest, 20 and 21 periods, fell 21 and 17 ms short of it, outside the 15 ms tolerance, and it saw 16 of the 20
descents its rule needs.

## The loop, as the card runs it

The governor only moves when the die starts below 65 °C, so the evidence is the seven cool-start runs of
21 September (E10), which contain 36 clock transitions.

**It hunts, and the missing hysteresis explains it.** In one run of ones from a 64 °C die (charted in A11) the
board never came near 65 W (it peaked at 56 W); what the loop kept crossing was the 65 °C line. At a reading of 66 °C the clock
steps down; once the whole-degree reading is back at 65 °C the thermal test no longer fires, the power test sees
38 W < 65 W, and the clock steps back up. The clock changed seven times in 2.4 s, reaching 800 MHz twice, 1.6 s
apart. (**0.20.0:** on the cards' build the down-steps are the thermal loop's, one point per 0.4 s while the mean reads
66 or more; when it reads 65 the loop exits to the boot point, and on the next pass the power branch climbs straight back
to 800 MHz. The missing dead band is the same; in E51's development runs 82 of 82 up-steps while hunting came from a
reading of 66 or less, none from 67 or more, and in its frozen validation 92 of 92 from 65 or less: TH3 survived.) Then, with the die settled at 66 °C, it stayed at 600 MHz for the last 4.5 s. Over the whole 7.4 s run it
spent 5.6 s at the bottom point, 1.0 s at 700 MHz and 0.8 s at 800 MHz.

**Most down-steps can be attributed**, and the mix is informative:

| Cause | Count | Signature |
|---|---|---|
| Thermal only | 7 | die above 65 °C while the board drew 45–56 W, well under the limit |
| Thermal and power together | 4 | random data at 800 MHz, up to 88 W |
| Unattributed (reading ≤65 °C) | 7 | die 65 °C (once 64), board 34–56 W, so neither test fired on the values sampled. One (run 1, zeros, at 5.95 s: 800→600 MHz in a single step) looks like the boot-point reset; the other six are single-point steps in pairs 0.4–0.5 s apart, most likely thermal steps on passes where the service processor read 66 °C between our 10 Hz samples. Launches run back to back every 0.37–0.49 s, so every step is near a kernel boundary, which explains nothing. **0.20.0:** a pair 0.4–0.5 s apart is one loop period, and a 700→600 step at a reading of 65 is the loop's exit to the boot point (E51 development: the 700 MHz dwell of 26 of 26 descents lay in 0.3–0.7 s, median 0.5 s; its validation's 16 of 16 too) |
| Power branch acting alone | **0** | on this card only random data at 700–800 MHz exceeds 65 W, and it takes the die through 65 °C within half a second |

**It is slow to start.** The first clock change came a median 0.7 s after a block of launches began (0.14–2.01 s over
31 starts on 21 and 23 September; 0.39–0.99 s in E10's seven runs), about five passes of the loop under our 10 Hz
sampling (about 160 ms a pass). The service processor hears of a kernel's start or end only at the master minion's
heartbeat, about 1.05 s apart in the SP's own time (read from aifoundry3's 22 September ring; the source comment implies
100 s), which fits; E51's development launches reached 800 MHz a median 0.9 s after the launch (at most 1.11 s, 14
launches), and its frozen validation's a median 0.67 s (at most 1.2 s, 22 launches), so TH4, the heartbeat's latency,
survived. Once moving, it changed the clock a median 0.4 s after the previous change (0.1–0.8 s for the middle 80%);
eight of E10's 18 up-steps (50 of 120 over both days) go straight from 600 to 800 MHz between two 100 ms samples, faster
than one table point per pass. The `353f20e` source does not explain that; the cards' 0.20.0 governor climbs to the top
point in one call (E51 development: 57 of 57 climbs showed at most one 700 MHz sample, 33 none; its validation 67 of
67, 44 none).

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

Leakage at 80 °C is **20–29 W: 55–80% of an idle card and 31–45% of a 64 W random-data matmul** (the best fit's
23.3 W is 65% and 36%; `dvfs.json` `leak_fraction.idle_80c_law`; a range since version 3, because the idle readings fix
the slope and not the split). That is above Kanter's 5–30% at idle; under load, above 30% is not established (E44,
IDLE-k). Three things make it so high, and only the third is the chip's own: (1) it runs at 0.52 V
rather than the 0.4 V Esperanto designed for; (2) aifoundry2's desktop chassis rests it at 62–74 °C (66–67 °C on
27 September), not in server airflow, and these shares are quoted at 80 °C; (3) it carries 128 MB of shire SRAM (4 MB in each of 32 compute shires; Esperanto quotes over 160 MB on
die) with no array power gating in play.

## Consequences

- **The equation is right; it is just not what the loop uses.** Its activity term is strongly confirmed here:
  power over idle is close to linear in active minions (on aifoundry2 24.3 mW per minion at 256 active, 25.1 at 512
  and 26.5 at 1,024, four runs per count on 26 September; on aifoundry3 19.4, 21.8 and 24.1, on aifoundry1's card 1
  21.8, 24.3 and 27.2, so there the cost per minion rises more with the count; one session of 21 September had given
  25.6–27.0 mW on aifoundry2), and a model counting four classes of switching event predicts board power across fourteen
  operand patterns to 0.50 W rms, leaving one pattern out
  ([11-thermal-model.md](11-thermal-model.md)). The V²f term is only weakly testable, because the governor
  will not hold the high operating point long enough on a heavy workload.
- **Kanter's argument that measurement is expensive is weaker for this card, though it does not vanish.** His
  reason MLPerf cannot mandate measured power is that submitters will not pay to instrument a system. This chip is
  already instrumented as a load-bearing part of its own safety loop: a PMIC that meters the board, a service
  processor that reads it every pass, and a management interface that hands the number to the host. The cost of
  reporting the card's own power here is one query. MLPerf's measured power is the whole system (host, power supply,
  cooling), which this meter does not see, and the card's meter takes a new board value once per service-processor
  pass (133, 224 and 135 ms on aifoundry2, aifoundry3 and aifoundry1's card 1 with nothing polling; 156, 263 and
  158 ms under a 10 Hz sampler: E41), with the rails behind the PMIC's running average (τ ≈ 1.2 s; superseded by E58: 1.01–1.10 s, one SP pass late; 0.54 s on aifoundry1's card 1's SRAM rail).
- **A provisioned-power metric cannot see the hunting.** Normalising by nameplate kilowatts scores a card by
  its rating, while on this card a badly damped governor moves real throughput by tens of percent inside a
  single 7-second run.
- **The hunting measured here is at the thermal threshold**, which has no dead band in either version of the
  source. The two power-guardband macros that `353f20e` leaves unused (the older governor uses one of them) would not
  damp it; damping it needs a temperature dead band.

## The second card answers the open question, and raises a new one

aifoundry3 runs the same firmware and never leaves 600 MHz, on a die that rested at 50–58 °C on 22–24 September and
55–57 °C since 25 September (the version-3 check heated it to 88–90 °C, E44). Its
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

**Since then its governor has fallen silent.** The three-card check (E41, TEL-G) found no governor line at all in
aifoundry3's trace, and so the 22 September pattern rests on that one window. The 0.20.0 source predicts it: at a TDP of
0 the first kernel after boot enters a power-down loop that can never exit (its exit test is an average below
1.05 × 0 W, or 300 MHz), so the power task spins; the first time the mean then exceeds 65 °C, the dm pass sets the
thermal state, which nothing clears, and both branches stay locked with no line ever logged again. E51 read aifoundry3's
throttle residencies once, read-only, on 28 September: the power-up, power-down, thermal-down and power-safe states all
at 0 after 2 days 8 hours of uptime, although the heat-placement work of 27 September had taken its die past 66 °C, as
the latch predicts (**development, one reading**; the latch itself is read from the source, not established).

**And it shows the loop has no floor check.** The governor never asks whether its threshold is sane. A TDP of
zero is not rejected at init, not logged as a warning, and not visible to the host: the driver's
`ETSOC1_IOCTL_GET_DEVICE_CONFIGURATION` reports 65 W on all three machines. The card runs at the bottom of its
VMIN table (the firmware's table of operating points) for as long as its TDP stays at zero, and the only
symptom is that it is slow. (Correction, 2026-09-25: the zero is not flashed. A boot service on aifoundry3,
`et-board-clock-guard.service`, sets the static TDP level to 0 and the clocks to 600/400 MHz at every boot; see
[14-card-behaviour.md](14-card-behaviour.md).)

## Not established

- Whether the taped-out ET-SoC-1 drives its sleep transistors under some other firmware or in some other power
  state. The chip-level netlist is not in the open drop; the RTL statement covers the Erbium configuration, and
  the card corroborates it only in the sense that nothing observable uses it.
- What the boot frequency is set to in flash.
- ~~Why aifoundry3's flashed TDP is 0 W.~~ Answered on 2026-09-25: the lab's boot service sets it at every boot
  (above; 14-card-behaviour.md).
- Whether aifoundry3's lower switching power is silicon, package or board regulator. It was 8% by the 22 September
  transfer; since the three-card check, the model factor is 0.93–0.95 at aifoundry3's own launch temperature against
  0.96–0.99 on aifoundry2 (the DVFS page, §6), and aifoundry3 switches 0.958–0.969 of aifoundry2 at the same die
  temperature, 3–4% less (the Horace experiment, §10). Neither the
  third card nor the two-temperature test (E40) separated the card from its temperature.
- The wake-up probe can only detect a penalty larger than about ten cycles, for arrays idled up to 27 ms (the
  widest the delay op encodes). A gating policy with a longer timer would not show up.
- **Exactly which firmware build the cards run.** aifoundry3's service processor prints log lines that exist only in
  et-platform firmware before commit `60b40c10f` (24 September 2024, "Dvfs fixes and refactoring"), which reworked this
  governor; both cards report release 1.3.1, whose service-processor firmware is BL2 0.20.0, and the closest public
  source is `ffca4cbb4` (= `cafe03fc3^`, 17 May 2024). In that governor the power guardband is used, throttle events
  are logged once per state change, a step-up climbs to the top point in one call, and the thermal response is the
  blocking loop above. E51's development data fit it and not `353f20e` (the 0.4053 s grid, thermal entries on an idle
  card, the one-call climb); its frozen validation (28–29 September) left that theory (TH2) untested: two of its 46 idle
  loop intervals fell 17–21 ms off the grid, and it saw 16 of the 20 descents it needs. The loop section above describes
  `353f20e`; [14-card-behaviour.md](14-card-behaviour.md) has the cards' build.
- **Whether the governor acts on the mean or on the hottest sensor, by a registered test.** The source says the mean.
  E51's frozen validation left TH1 untested: 7 of 9 separating runs fitted the mean where the rule asks for 80%, and 4
  idle cycles separated the two where it asks for 5; none fitted the hottest sensor.
- **Whether placement delays the first step on aifoundry2** (the owner's second question). In each of the validation's 4
  complete blocks the perimeter held 800 MHz longer, 1.16–1.52 times, but 4 blocks give the log ratio a 99% interval of
  [−0.11, 0.61], and the test needs 6. The card idled at 71–76 °C for most of the window, so the three
  sessions the plan allows could start only in an evening cool spell, and each ended when the card no longer cooled
  back to its 62 °C starting edge.

## Related

- [11-thermal-model.md](11-thermal-model.md): the leakage law this page re-checks after a day's idle.
- [14-card-behaviour.md](14-card-behaviour.md): the three machines side by side, and how to measure without the
  governor moving the clock.
- [13-why-low-power.md](13-why-low-power.md): the operating points against an A100, term by term.
- [03-experiments.md](03-experiments.md): E10, E18, E19, E21, the note on E10 re-analysed, and E51 (the DV2
  development night of 28 September and its frozen validation of 28–29 September).
