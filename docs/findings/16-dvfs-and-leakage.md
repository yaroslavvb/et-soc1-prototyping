# Finding: the DVFS loop measures power instead of estimating it, and never switches leakage off

**Sources:** R9 (David Kanter's claims), R3 (firmware at `353f20e`), R2 (open RTL at `b38a1a3`), E10
(the governor in action), E18 (the wake-up probe), E19 (a 20-hour idle check). Published as A11.

David Kanter, who runs MLPerf, described how a mature chip regulates its own power. Six of his statements are
checkable against this chip. Four hold, one is wrong for this part, and one is a capability that ships
switched off.

| What he said | Verdict | Evidence |
|---|---|---|
| A mature design runs a DVFS loop that steps V and f to stay inside an envelope | **Confirmed** | Three operating points: 600 MHz at 0.517 V, 700 at 0.568, 800 at 0.618. Voltage moved with frequency in all 36 observed transitions |
| The chip counts bus bits and execution-unit activity and computes its own power estimate, on millisecond timescales | **Not on this chip** | The loop reads a measured PMIC wattage and a PVT temperature. No activity counter appears anywhere in it. He hedged "maybe not on Esperanto's part"; the hedge was right |
| Thermal sensors are in the same loop, because leakage depends on temperature | **Confirmed, and thermal wins** | The temperature test runs before the power test; 7 of 18 down-steps were thermal-only |
| Cache arrays sit behind leakage-suppression transistors, un-suppressed on demand at a small wake-up latency | **Built, not used** | Per-minion sleep and isolation exist in the RTL, tied off in the open configuration, driven by no firmware line, and no wake-up latency is measurable |
| Leakage is typically 5–30% of a design's power, ~20% common | **This card is worse** | 36% of a busy card, 64% of an idle one at 80 °C |
| Leakage costs power, not correctness | **Confirmed** | 20.4 h of idling cost 31.8 W and produced no errors |

---

## The loop, as the firmware builds it

The whole governor is `check_power_throttle_conditions()` in
`ServiceProcessorBL2/services/thermal_pwr_mgmt.c`, called once per pass of the device-management task
(`DM_TASK_DELAY_MS` = 10 ms):

```
T = pvt_get_minion_avg_temperature()      # on-die thermal sensor
P = pmic_read_average_soc_power()         # MEASURED board power, from the PMIC over I2C
if active_power_management and master minion is BUSY:
    if   T > 65 °C and f > f_min:  step DOWN one VMIN-LUT point
    elif P > 65 W  and f > f_min:  step DOWN one VMIN-LUT point
    elif P < 65 W  and f < f_max:  step UP   one VMIN-LUT point
on master minion going IDLE:  set frequency back to the boot point
```

Four consequences, all of which show up in the measurements:

- **The input is a measurement.** Nothing counts activity. Kanter's *P = C × V² × f* is never evaluated by
  this firmware, because the chip does not have to infer power — it has a meter.
- **Thermal has priority**, and it is a plain `if`, so above 65 °C the power branch is unreachable. A card that
  has been busy idles above 65 °C and is therefore pinned at its lowest operating point no matter how little
  power it draws. This is why the earlier work saw a card that "never changes clock".
- **There is no hysteresis.** `UPPER_POWER_THRESHOLD_GUARDBAND` and `LOWER_POWER_THRESHOLD_GUARDBAND`, a ±5%
  dead band, are **defined in the file and never used**. Dead code at this commit.
- **The clock resets at every kernel boundary**, because an idle master minion sends the frequency back to the
  boot point.

## The loop, as the card runs it

The governor only moves when the die starts below 65 °C, so the evidence is the seven cool-start runs of
21 September (E10), which contain 36 clock transitions.

**It hunts.** With a ~2 s averaged power input, no dead band, and one-point steps, the loop climbs until it
trips a threshold, drops, sees the threshold clear and climbs again, with a period of about two seconds. Over a
single 7-second run of constant data the clock changed seven times.

**Every down-step is attributable**, and the mix is informative:

| Cause | Count | Signature |
|---|---|---|
| Thermal only | 7 | die above 65 °C while the board drew 45–56 W, well under the limit |
| Thermal and power together | 4 | random data at 800 MHz, up to 88 W |
| Kernel boundary, not throttling at all | 7 | 12–186 ms from a launch boundary, at 64–65 °C and 33–39 W |
| Power branch acting alone | **0** | on this card the only way past 65 W is 800 MHz, by which point the die is already past 65 °C |

**It is slow to start.** The first clock change came 0.39–0.99 s after a kernel launched, never in
milliseconds, though the task itself runs every 10 ms.

## Leakage suppression: present, tied off, undetectable

**The hardware exists.** The neighbourhood RTL carries a per-minion sleep control and its acknowledge
(`pwr_ctrl_min_nsleepin` / `nsleepout`, one bit per minion), a global pair, per-minion isolation
(`pwr_ctrl_min_isolate`), level shifters and a power stub that forces outputs safe while a domain is down —
a textbook power-gating structure at exactly the granularity Kanter described.

**Nothing drives it.** In the open configuration the whole interface is tied off, with a comment saying so:

```verilog
// Power Ctrl - power control handled outside cpu subsystem and this ifce is not used
.pwr_ctrl_glb_nsleepin ('1),   // '1 = never asleep
.pwr_ctrl_min_nsleepin ('1),
.pwr_ctrl_min_isolate  ('0),
```

The service-processor firmware, searched at the card's own commit, contains no power-gating control of any
kind. The only `PWR_CTRL` matches in the tree are an eMMC controller's bus voltage.

**And the card shows no sign of it (E18).** If an array were suppressed once idle, the first access afterwards
would pay the wake-up. The probe placed one line at a chosen level, spun the minion on its cycle counter for
1.7 µs to 27 ms without touching that line, then timed a single load — same line, only the idle time varying,
20 repeats:

| Level | Longest idle minus shortest |
|---|---|
| L1 | **0 cycles** |
| L1 after an evict to L1 | **0 cycles** |
| L2 | −11 cycles (slightly *faster*; noise) |
| L3 | **0 cycles** |
| DRAM | +10 cycles — the row closing, worth ~40 cycles, already characterised in the memory work |

So the only gating actually working on this card is **clock** gating, which the same RTL uses aggressively
(per lane, per functional unit, with a seven-cycle tail). That is why an idle-but-powered core costs almost no
dynamic power and still leaks.

## What it costs, and a free validation

After **20.4 hours** of complete idleness (E19), in a warmer room than the day before:

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

Leakage is **36% of a 63 W random-data matmul and 64% of an idle card at 80 °C**, against Kanter's 5–30%.
Three things cause it and only one is the chip's fault: it runs at 0.52 V rather than the 0.4 V Esperanto
designed for, in a desktop chassis that idles it at 73–80 °C rather than in server airflow, with 160 MB of
on-die SRAM and no array power gating in play.

## Consequences

- **The equation is right; it is just not what the loop uses.** Its activity term is strongly confirmed here:
  power over idle is linear in active minions, and a model counting four classes of switching event predicts
  board power across fourteen operand patterns to 0.5 W out of sample
  ([11-thermal-model.md](11-thermal-model.md)). The V²f term is only weakly testable, because the governor
  will not hold the high operating point long enough on a heavy workload.
- **"Measurement is expensive" does not apply to this card.** Kanter's reason MLPerf cannot mandate measured
  power is that submitters will not pay to instrument a system. This chip is already instrumented as a
  load-bearing part of its own safety loop: a PMIC that averages board power, a service processor that reads it
  every 10 ms, and a management interface that hands the number to the host. Reporting measured power costs one
  query.
- **A provisioned-power metric cannot see the hunting.** Normalising by nameplate kilowatts scores a card by
  its rating, while on this card a badly damped governor moves real throughput by tens of percent inside a
  single 7-second run.
- **The fix is already in the source**: two guardband macros, defined and unused.

## The second card answers the open question, and raises a new one

aifoundry3 runs the same firmware and never leaves 600 MHz, on a die 15 °C below the thermal threshold. Its
service processor reports a **static TDP of 0 W** where aifoundry2 reports 65 W (E21). In
`check_power_throttle_conditions()` the step-down test is `measured power > TDP` and the step-up test is `<`,
so at zero the first is a tautology and the second is unreachable. The card's own trace buffer holds 26
throttle-down events and no step-up events in one 8 KB window, each printing `tdp level: 0`.

**This establishes what this brief could not.** The power branch had never fired alone on aifoundry2, because
a card that has been busy idles above 65 °C and the thermal test comes first, so the brief listed it as
unverified. On aifoundry3 it is the only branch that ever fires, and it behaves exactly as written.

**And it shows the loop has no floor check.** The governor never asks whether its threshold is sane. A TDP of
zero is not rejected at init, not logged as a warning, and not visible to the host: the driver's
`ETSOC1_IOCTL_GET_DEVICE_CONFIGURATION` reports 65 W on all three machines. The card runs, forever, at the
bottom of its VMIN table, and the only symptom is that it is slow. The same guardband macros that would give
the loop hysteresis would also have given it a place to notice this.

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
