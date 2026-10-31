# Q130(d) — the governor's thermal branch, read at the build aifoundry2 runs (BL2 0.22.0)

Sat 31 Oct 2026 (week 44). **Desk only: no card was opened, claimed or set for this.** A source read of the
firmware arm that turns heat into clock, at the revision that matches the build aifoundry2's card reports,
with every statement checked against the service-processor traces E64 and E69 already committed.

Everything about the governor the lab has written at **0.22.0** so far is about its **power** arm: the
throttle-wrap gate ([`../2026-10-27-q129-throttle-wrap-gate/`](../2026-10-27-q129-throttle-wrap-gate/README.md)),
the two set paths, and E72's TDP pin
([`../../../findings/14-card-behaviour.md`](../../../findings/14-card-behaviour.md) § "The governor's two knobs").
The **thermal** arm was last read at 0.20.0, in
[`../2026-09-28-dvfs2-aifoundry2/plan/review-governor.md`](../2026-09-28-dvfs2-aifoundry2/plan/review-governor.md),
a build this card turned out not to be running. This fills that hole, so the blog can say how heat becomes a
clock and not only how power does.

The firmware is open source. Citations are `repo@revision:path:line`; `TPM` abbreviates
`device-bootloaders/src/ServiceProcessorBL2/services/thermal_pwr_mgmt.c` and other BL2 paths are relative to
`device-bootloaders/src/ServiceProcessorBL2/`.

| Tag | Revision of `aifoundry-org/et-platform` (Apache-2.0) | What it is |
|---|---|---|
| **`@22`** | `836a4ab600e93c3059bb58c898edbc37744cd8d0` (2026-07-17), `device-bootloaders/CMakeLists.txt:4` = `VERSION 0.22.0` | the in-development 0.22.0 line; the source for the BL2 0.22.0 the card reports |
| **`@21`** | `50310b06` (2024-09-25), "[device-bootloaders] Close development of version 0.21.0", `CMakeLists.txt:11` = `0.21.0` | where the single-pass governor was already in place |
| **`@20`** | `ffca4cbb436713cffcbc5028fc9a86529dc86c7c` (2024-05-17), "Close development of version 0.20.0", `CMakeLists.txt:11` = `0.20.0` | the loop governor the 27 Sep review read |
| **`@18`** | `da192816a73a6636e7b7a6878dcd4b1e4340c88f` (2024-03-27), "Close development of version 0.18.0", `CMakeLists.txt:11` = `0.18.0` | aifoundry1's card 1 |

## Results first

1. **The thermal arm is one strict integer comparison, once per management pass, and it steps one VMIN point.**
   `if (temperature_updated && (temperature_C > temperature_threshold_C)) { if (f > f_min) { log; notify
   POWER_DOWN; } }` — `@22:TPM:884-896`, called from `rtos_task/dm_task.c:267`. The number compared is the
   integer mean of the 34 minion-shire sensors, each truncated to a whole degree, faults left out
   (`@22:driver/pvt_controller.c:1274-1301`). The threshold defaults to 65 °C
   (`@22:include/thermal_pwr_mgmt.h:41`). There is no per-sensor path and no hottest-sensor path.

2. **There is no hysteresis, no step delay and no guard band — and the dead band is one integer degree.** Entry
   is `T > thr`; the only way back up is the power arm, which sits in the same `else if` chain
   (`@22:TPM:898,910`) and is therefore reached only when `T ≤ thr`. `DELTA_TEMP_UPDATE_PERIOD` (1000) is
   defined at `@22:include/thermal_pwr_mgmt.h:86` and **used nowhere in the tree**;
   `UPPER_/LOWER_POWER_THRESHOLD_GUARDBAND` are defined at `@22:TPM:217,223` and used nowhere — whereas at
   `@20` the upper guard band is live, in the power loop's exit test (`@20:TPM:2241`). The only damping left
   at 0.22.0 is the pass itself.

3. **The thermal arm wins the pass even when it cannot act, and that is what the 600 MHz clamp is.** The inner
   guard `minion_curr_frequency > minion_min_frequency` (`@22:TPM:886`) stops the step at the VMIN floor —
   but the *outer* test has already claimed the `else if` chain, so while the mean reads above the threshold
   the power arm never runs and **cannot lift the clock**, and nothing is logged. A card whose floor power
   still overheats it therefore sits at 600 MHz in silence, with the die floating above the threshold. That is
   measured: fp32 random sustained holds 600 MHz at a die of 67.1 °C and 54.4 W
   ([`../2026-10-23-e64-horace-power-limit/README.md:94`](../2026-10-23-e64-horace-power-limit/README.md)).

4. **Nothing latches the thermal arm at 0.22.0.** `struct soc_power_reg_t` (`@22:TPM:174-193`) has **no**
   `power_throttle_state` member; the throttle state is a local of the power task (`@22:TPM:2231-2232`) and
   `check_power_throttle_conditions` never reads it. At `@20` every dm-task write required
   `state < THERMAL_DOWN` (`@20:TPM:669,845`) and the thermal loop's three error returns
   (`@20:TPM:2313`, `:2328`, `:2340`) left the state at 4 with no path out but an SP reset. That latch mechanism does not
   exist on this card's build.

5. **The thermal arm is byte-identical from 0.21.0's close to 0.22.0, so the power arm's wrap hazard cannot
   reach it.** `diff @21:TPM @22:TPM` is 142 lines, and inside `check_power_throttle_conditions` the only
   change is SW-22147's width fix on the two **power** locals — `uint16_t avg_soc_pwr_mW` → `uint32_t` and
   `int32_t tdp_level_mW` → `uint32_t` — plus one blank line (the fix itself is `47827533`, 2024-11-26, which
   is why the 0.22.0 changelog carries it under `[Unreleased]`). Q129's gate argued this from one revision;
   it is now a diff. The thermal arm's own operands are `uint8_t` throughout and were never narrowed.

6. **The single-pass governor is 0.21.0's work, not 0.22.0's.** `60b40c10fbf40fa657a0da778263648789a859ff`
   (2024-09-24, "[SW-21898] Dvfs fixes and refactoring"), which 0.21.0's changelog lists as "Power and thermal
   throttling fixes and refactoring"; 0.21.0 closed at `50310b06` and 0.22.0 opened at `ce729715` in the same
   minute, 2024-09-25. So "the rewritten governor" and "what the card runs" are the same code, and the two are
   one release apart, not two.

7. **The committed E64 ring already proves the card ran 0.22.0 on 23 October — four days before E69 read its
   version string.** Three independent signatures, over 76 runs and 3,001 parsed ring entries (1,040 `New OP:` lines, 1,033 power-status records, 542 power-ups, 224 power-downs, 162 thermal steps)
   ([`trace-tests.json`](trace-tests.json)):
   - every power-status record a thermal step writes carries `throttle_state = 2`, **162 of 162**. At 0.22.0's
     enum (`@22:device-api/include/management-api/device_mgmt_api_spec.h:280-283`: IDLE 0, UP 1, DOWN 2,
     SAFE 3) that is POWER_DOWN, which is exactly what the thermal arm notifies (`@22:TPM:894`). At 0.20.0's
     seven-state enum a thermal step writes **4** (THERMAL_DOWN) and a power-up writes 2; here power-ups write
     **1**, 542 of 542. No state above 2 appears anywhere.
   - **zero** `Thermal idle state event` lines, in a parser that looks for them
     (`tools/claims-v3/hp/sptrace_events.py:43`). At 0.20.0 every completed thermal episode writes that
     CRITICAL line (`@20:TPM:2371-2373`); at 0.22.0 there is no thermal loop and no such string.
   - the 1,040 operating-point lines all match `New OP: Freq %d MNN %d (V) SRM %d (V)`
     (`tools/claims-v3/hpl/sptrace_full.py:38`), the `@22:TPM:1858-1863` string. 0.20.0's is
     `new OP: Freq %d MNN voltage %d SRM voltage %d`.

8. **Every predicate the source read implies holds on the card.** From the same 76 runs:

   | # | what the source says | where | what the rings show | verdict |
   |---|---|---|---|---|
   | T1 | the test is strict `>` on integers, so the first tripping reading is `thr + 1` | `@22:TPM:884` | at threshold 65 the printed temperature is **66** (151) or 67 (3); at threshold 62 it is **63** (8). **Never equal to the threshold, never below it** | PASS |
   | T2 | a thermal step is exactly one VMIN point | `@22:TPM:1888-1906`, `driver/flashfs.c:2384-2399` | **800→700** (79) and **700→600** (82). No 800→600, no sub-600 target | PASS |
   | T3 | no step at the floor | `@22:TPM:886` | **0 of 162** thermal steps taken while the clock was already 600 MHz | PASS |
   | T4 | the step is requested as POWER_DOWN | `@22:TPM:894` | state 2 after 162/162 thermal steps; state 2 after 224/224 power-downs; state 1 after 542/542 power-ups | PASS |
   | T5 | no thermal loop, so no thermal-idle line | 0.22.0 has no `thermal_throttling()` | 0 such lines | PASS |
   | T6 | the idle line carries no numbers at 0.22.0 (INFO) | `@22:TPM:3117` vs `@20:TPM:853-855` | **no `Power idle state event` line of either form is in these rings** | UNTESTED — the 4 KB ring holds under a second at INFO with a sampler, and the harness dumps during work |
   | T7 | the arm can act at most once per dm pass | `rtos_task/dm_task.c:267,275` | successive governor decisions are **≥ 0.16 s** apart, median 0.21 s; consecutive thermal steps ≥ 0.20 s, median 0.46 s. A step lands 0.02–0.14 s (median 0.05) after its own line | PASS |
   | T8 | the ratchet: thermal gives one point back per trip, power takes one back per pass | `@22:TPM:884-920` | the only pair following a thermal step is `thermal_down → power_up`, **132 of 132** (plus 27 `thermal_down → thermal_down`). A thermal step is never followed by a power-down | PASS |

9. **The sustained clamp is a constant-POWER clamp at 49.2–51.4 W of board power, and that one band explains
   the whole kinds-of-numbers column** ([`clamp-band.json`](clamp-band.json),
   [`clamp_model.py`](clamp_model.py)). Because the arm is bang-bang on the integer mean, the steady state puts
   the die *on* the trip, so the board power sits where E64's own thermal line puts the trip:
   `board_W = (trip_C − 41.88) / 0.4696`
   ([`../2026-10-23-e64-horace-power-limit/surface.txt:27`](../2026-10-23-e64-horace-power-limit/surface.txt)).
   The trip is a band in whole degrees — 65 is the last reading that passes, 66 the first that trips — so the
   clamp is **49.23 W to 51.36 W**, 2.13 W wide. Each kind then gets whatever clock puts *its* power in that
   band:

   | type/kind | board W at 600 | at 800 | sustained W | die °C | sustained MHz | share at 800 | the band's clock | regime |
   |---|---:|---:|---:|---:|---:|---:|---|---|
   | fp32/zeros | 27.0 | 36.4 | 36.4 | 59.0 | 800 | 1.00 | 800 | never trips |
   | fp16/zeros | 27.4 | 36.4 | 36.1 | 59.0 | 794 | 0.97 | 800 | never trips |
   | int8/zeros | 27.9 | 37.6 | 37.6 | 59.0 | 800 | 1.00 | 800 | never trips |
   | int8/ones | 29.9 | 41.7 | 41.8 | 61.7 | 800 | 1.00 | 800 | never trips |
   | fp16/ones | 45.4 | 54.6 | 49.3 | 65.4 | **737** | 0.48 | 684–730 | in the clamp |
   | fp32/ones | 45.2 | 54.4 | 49.4 | 65.4 | **738** | 0.48 | 688–734 | in the clamp |
   | int8/randn | 44.4 | 53.2 | 50.7 | 65.3 | **763** | 0.66 | 710–759 | in the clamp |
   | fp16/randn | 51.5 | 63.9 | 51.3 | 66.1 | **600** | 0.00 | 600 | the floor is already over the band |
   | fp32/randn | 54.3 | 67.8 | 54.4 | 67.1 | **600** | 0.00 | 600 | the floor is already over the band |

   Residual against the band's top: 0, −6.0, 0, 0, +6.6, +4.4, +4.3, 0, 0 MHz — rms **3.6 MHz** over the nine
   cells and **5.2 MHz** over the three that discriminate. 🛑 **This is not a prediction and must not be read
   as one:** each cell's bracket uses that same run's own median board power at 600 and at 800 MHz, so it is
   in-sample by construction, and it is linear in frequency where the real curve is not. It is a
   *decomposition* — it says the clamp is a power clamp at the trip and that the trip's integer width is worth
   2.1 W — next to which E64-T1's **out-of-sample** 4.8–9.6 MHz over the same nine cells
   ([`../2026-10-27-q129-governor-temperature/README.md:76-87`](../2026-10-27-q129-governor-temperature/README.md))
   is the honest accuracy number. The two agree on the mechanism: T1's two free parameters are γ and **the
   trip**, and it sweeps the trip over exactly {65.5, 66.0} °C because of the integer truncation this read
   pins to `@22:driver/pvt_controller.c:577`.

10. **E69 is the experiment that moved the band, and it moved as this read says it must.** At the card's own
    65 °C the sustained `ones` cell holds **763.4 MHz** with **11 thermal throttle-down events and 0 power
    steps**, die pinned at 65.2 °C in every one of the last twenty 2 s bins, 51.9 W; raise the threshold five
    degrees and the same work holds **800.0 MHz in every bin for 76 s with 0 thermal steps**, die 64.2 °C,
    54.7 W ([`../2026-10-27-e69-governor-knob/README.md:63-79`](../2026-10-27-e69-governor-knob/README.md)).
    The band at a 70 °C trip is 59.9–62.0 W, which is above this cell's 800 MHz power, so the clamp vanishes —
    which is what "the sustained gap is 36.6 MHz and it belongs to the threshold" means mechanically. The
    800.0 MHz figure is a **ceiling artefact** (800 is this card's top VMIN point), as E69 itself says; the
    step counts and the 800-share are the content.

## The thermal test at 0.22.0, line by line

All at `@22`, paths relative to `device-bootloaders/src/ServiceProcessorBL2/`.

| Item | What it is | Where |
|---|---|---|
| the compared value | `uint8_t temperature_C = g_pmic_power_reg.soc_temperature;` | `TPM:867` |
| its writers | the dm pass, from `pvt_get_minion_avg_temperature()`; **and every host `GET_MODULE_CURRENT_TEMPERATURE`**, which stores `pvt_temperature.current` — the same mean, read fresh at query time | `TPM:698` and `TPM:754` |
| the aggregate | integer mean over shires 0–33, divided by the **valid** count; a faulted sample is left out | `driver/pvt_controller.c:1274-1301` |
| the sensors | 34 minion shires (`PVTC_MINION_SHIRE_NUM 34`); shire *i* → PVT *i*/8, TS *i*%8; the I/O shire's sensor is a separate reader and is **not** in the mean | `include/bl2_pvt_controller.h:75`; `driver/pvt_controller.c:645-657`, `:659-665` |
| the per-sensor conversion | `(G + (H·N)/CAL5 − H/2) / 1000` in `int`, so **truncated to whole °C**; run mode 1, G/H/CAL5 = 57400/249400/4096, no per-die fuse calibration | `driver/pvt_controller.c:567-585`; `include/bl2_pvt_controller.h:97,157,162,167` |
| the fault path | a `SAMPLE_FAULT` bit returns `ERROR_PVT_SAMPLE_FAULT` before any conversion | `driver/pvt_controller.c:628-632` |
| no hottest-sensor path | `g_soc_power_reg.max_temp` is declared and only ever **read** — never assigned anywhere in the tree | `TPM:182`, `:1380-1382`, `:2352` |
| the threshold | `temperature_threshold.sw_temperature_c`; default `TEMP_THRESHOLD_SW_MANAGED` **65**; host-settable to any `uint8`; in plain SP `.data` RAM, so lost at an SP reset | `include/thermal_pwr_mgmt.h:41`; `TPM:143-144` |
| **the test** | `temperature_updated && (temperature_C > temperature_threshold_C)` — **strict, integer, no hysteresis** | `TPM:884` |
| `temperature_updated` | the pass's own flag: `true` at the top of every pass, cleared only if `update_module_current_temperature()` returned non-zero | `rtos_task/dm_task.c:198,206-212` |
| **step direction and size** | down only, one VMIN-LUT entry; the helper refuses any target above the current frequency; at index 0 the previous point *is* the current one and the setter returns success without acting | `TPM:894` → `:2182-2186` → `:1888-1906`; `driver/flashfs.c:2384-2399`, `:2392`; `TPM:1800-1803` |
| the step's order | **down: PLL first, then voltage** (up: voltage first, then PLL); each real change writes a power-status record and one CRITICAL `New OP:` line | `TPM:1832-1849`, `:1856`, `:1858-1863` |
| the LUT | 11 slots, of which this card fills **3**: 600/700/800 MHz, so one step is **100 MHz**. The matching die voltages, 516–518 / 568 / 618–620 mV, are E10's telemetry, not the LUT dump | `device-bootloaders/src/shared/common/include/service_processor_BL2_data.h:87` (a repository-relative path, not a BL2-relative one); [`../2026-10-27-e72-600mhz/vmin-lut.json`](../2026-10-27-e72-600mhz/vmin-lut.json) `.minion_frequency_points_mhz`; [`../../../findings/14-card-behaviour.md:145-147`](../../../findings/14-card-behaviour.md) |
| the setter's rounding | to `MODE_FREQUENCY_STEP_SIZE` = 25 MHz, because `USE_FCW_FOR_LVDPLL` is 0 | `TPM:1806-1809`; `etsoc-hal/include/hwinc/lvdpll_defines.h:66` (repository-relative); `include/config/mgmt_build_config.h:369` |
| **the floor** | the arm acts only while `f > mnn_frequency_min_limit`, the LUT's own minimum, read once at init | `TPM:886`, `:874`, `:1581-1600` |
| **the pass period** | once per dm pass, which then sleeps `pdMS_TO_TICKS(DM_TASK_DELAY_MS = 10)`; the pass is dominated by busy-waiting I2C, 133 ms unloaded on this card | `rtos_task/dm_task.c:267,275`; `include/config/mgmt_build_config.h:427`; [`../../../findings/14-card-behaviour.md:126`](../../../findings/14-card-behaviour.md) |
| the gates | `active_power_management == ON` **and** the master minion **not idle** — so an idle die gets no thermal response at all | `TPM:879-880` |
| the record each step writes | `throttle_state`, `power_state`, the PMIC **average** power in W, and a **freshly re-read** mean — the power task's own reading, not the dm pass's | `TPM:2061-2095`; `et-trace/include/et-trace/layout.h:399-418` |
| the hysteresis macros | `DELTA_TEMP_UPDATE_PERIOD`, `UPPER_/LOWER_POWER_THRESHOLD_GUARDBAND`: defined, used nowhere | `include/thermal_pwr_mgmt.h:86`; `TPM:217,223` |

### How it interacts with the power test

One `if / else if / else if` chain, in this order (`@22:TPM:884-924`):

1. **thermal** — `T > thr`: if `f > f_min`, log CRITICAL and notify POWER_DOWN. Either way, **the chain ends
   here**.
2. **power down** — `P_avg > TDP` and `f > f_min`: log CRITICAL and notify POWER_DOWN.
3. **power up** — `P_avg < TDP` and `f < f_max`: log CRITICAL and notify POWER_UP.
4. else a DEBUG line.

Three consequences the card shows:

- **Thermal has absolute priority, including the priority to do nothing.** At the floor with a hot die, branch
  1 is taken, its inner guard fails, and branches 2 and 3 never run. The clock is held at 600 MHz by the
  *absence* of an up-step, not by a down-step, and the ring stays silent. In E64's two floor-pinned cells the
  share of samples at 800 MHz is exactly 0.00 and the thermal share 1.00
  ([`../2026-10-23-e64-horace-power-limit/README.md:91,94`](../2026-10-23-e64-horace-power-limit/README.md)).
- **The two arms read different quantities with different time constants.** The thermal arm reads an
  instantaneous spatial mean of 34 sensors behind a thermal mass whose time constant E64-T1 fits at **14.0 s** on
  the SUS runs' own die rise (rms 0.2456 °C over 339 bins,
  [`../2026-10-27-q129-governor-temperature/figures-t1.json`](../2026-10-27-q129-governor-temperature/figures-t1.json)
  `.variants.*.tau_th.tau_th_s`);
  the power arm reads the PMIC's running **average** (`TPM:869-870`), which E64 fits as a first-order filter of
  τ = 1.3 s compared once per 0.24 s pass
  ([`../2026-10-23-e64-horace-power-limit/surface.txt:2`](../2026-10-23-e64-horace-power-limit/surface.txt)).
  So the power arm dithers on a 1.3 s memory and the thermal arm clamps on a 14 s one — an order of
  magnitude apart, which is why a burst is power-limited and a minute of the same work is heat-limited.
- **The ratchet is asymmetric, and that sets the duty cycle.** The thermal arm gives back one point per trip;
  the power arm takes one back on *every* pass where the mean is at or below the threshold. In the rings, the
  pair after a thermal step is `power_up` 132 of 132 times, and `power_up → power_up` runs 184 times — the
  two-pass climb 600→700→800 the review first saw at 0.20.0 survives here, but as two ordinary passes rather
  than one loop. The sustained mean clock is then the duty cycle of that ratchet, which is why `int8/randn`
  reads 763 MHz with 0.66 of its samples at 800 and `fp32/ones` reads 738 MHz with 0.48.

### What latches, and what does not

| Path | 0.22.0 | 0.20.0 / 0.18.0 |
|---|---|---|
| a sticky governor state in SP RAM | **none**: `struct soc_power_reg_t` has no `power_throttle_state` (`@22:TPM:174-193`); the state is a task local (`:2231-2232`) and the dm arm never reads it | `g_soc_power_reg.power_throttle_state`, and **every** dm-task write requires `state < THERMAL_DOWN` (`@20:TPM:669,845`; `@18:TPM:591,767`) |
| a failed step | `current_throttle_state` is left unchanged and the next pass tries again (`@22:TPM:2289-2293`) | the thermal loop's three error returns leave state 4 with no exit line and no residency update (`@20:TPM:2313,2328,2340`) — a latch nothing but an SP reset clears |
| SAFE | blocks a later DOWN (`@22:TPM:2261-2264`) but **UP is always allowed** out of it, and stepping up from 300 MHz goes to the LUT minimum (`:2267-2270`, `:1937-1941`) | terminal: nothing returns 5 or 6 (`@20:TPM:678,858,871,885,1699,2368,2486,2490`) |
| the safe state's effect | really programs 300 MHz, through the ordinary setter (`@22:TPM:2007-2010` → `:1794`) | cosmetic: the PLL change is guarded by `(status != STATUS_SUCCESS) && …` (`@20:TPM:2016`) and `Minion_Get_Voltage_Given_Freq(300)` always succeeds, so only the frequency register is written |
| a 0 W TDP | a **reversible pin** at the floor; writing the TDP back releases it on the next pass (E72) | the power loop can never satisfy `avg < 1.05 × 0`, so the power task spins for ever and the first 65 °C crossing latches THERMAL_DOWN (`@20:TPM:2173-2256`, `:668-679`) |

### The PMIC alarm rows

| Row | 0.22.0 | 0.20.0 and 0.18.0 |
|---|---|---|
| temperature alarm | `TEMP_THRESHOLD_HW_CATASTROPHIC` **75 °C** → `PMIC_I2C_TEMP_ALARM_CONF_ADDRESS`, one byte, with a 55–75 range check (`@22:driver/pmic_controller.c:1294-1305`, `:506`; `include/bl2_pmic_controller.h:281,286,291`) | identical constants and setter (`@20:driver/pmic_controller.c:490,1201`; `@20:include/bl2_pmic_controller.h:272,277,282`; the same at `@18`) |
| power alarm | `POWER_THRESHOLD_HW_CATASTROPHIC` **75 W** → `pmic_set_tdp_threshold(75)`, which **refuses a value at or below the live SW TDP**, subtracts the register's 15 W base, clamps the offset to 0x3F, shifts left 2 and writes **one** byte; the read-back is base + offset × 250 mW, so 75 W goes in as 240 and reads back as exactly 75 000 mW (`@22:driver/pmic_controller.c:509,2197-2224,2157-2175`; `include/pmic_hal.h:1009-1010`; `include/bl2_pmic_controller.h:262,267`) | 🛑 **a different write**: the caller passes `POWER_THRESHOLD_HW_CATASTROPHIC << 2` = 300 and the setter does **no base arithmetic and no clamp** — `set_pmic_reg(PMIC_I2C_PWR_ALARM_CONFIG_ADDRESS, (uint8_t *)&power_alarm, 2)`, a **two-byte** write starting at the one-byte alarm register (`@20:driver/pmic_controller.c:493,2089-2092`; the same at `@18:…:493,2020`). On a little-endian SP that puts 0x2C in the alarm byte and 0x01 in the byte after it. **What the PMIC does with either write is not established** — PMIC firmware 1.5.0 and 1.3.0 are closed — but the two builds do not program the same thing, and the older one touches a neighbouring register |
| when they are armed | in `enable_pmic_interrupts()`, called at the **end** of the SP boot sequence (`@22:common/main.c:552`), after `init_thermal_pwr_mgmt_service()` at `main.c:495` has set the 65 W SW TDP — which is why the "must exceed the SW TDP" guard passes. This move is the 0.22.0 changelog's SW-22053 | inside `setup_pmic()` itself (`@20:driver/pmic_controller.c:480-496`, called from `common/main.c:152`), before the SW TDP exists |
| the ISR's effect | over-temperature **or** over-power → one notification of POWER_SAFE (`@22:TPM:2317-2323`) | over-temperature → THERMAL_SAFE, else over-power → POWER_SAFE, written straight into the sticky state (`@20:TPM:2480-2497`) |
| what the alarm compares | the PMIC's own system-temperature register (`@22:driver/pmic_controller.c:1327-1330`) | the same register |
| whether it has ever acted | **no.** That register read 0 in all 281,951 V3 samples on all three cards, and die means of 103 °C (aifoundry2) and 115 °C (card 0) drew no response; board readings of 86–88 W did not visibly trip the power alarm either ([`../2026-09-28-dvfs2-aifoundry2/plan/review-governor.md:421-430`](../2026-09-28-dvfs2-aifoundry2/plan/review-governor.md)) | as above |

### What changed from 0.20.0 and 0.18.0

| | 0.18.0 (`@18`) | 0.20.0 (`@20`) | 0.22.0 (`@22`, this card) |
|---|---|---|---|
| where the thermal test lives | inside `update_module_current_temperature()`, i.e. at the top of the pass (`TPM:590-602`) | the same (`TPM:668-680`) | in `check_power_throttle_conditions()`, the pass's last step (`TPM:884-895`, `dm_task.c:267`) |
| thermal-first by | pass ordering: the temperature update runs before the power update | the same | an `else if` chain — the power tests are *skipped*, not merely later (`TPM:884,898`) |
| the test | `mean > sw_thr`, integer, strict | the same | the same |
| a busy-kernel gate on the thermal arm | **no** | **no** | **yes**: `get_mm_state() != MM_STATE_IDLE` (`TPM:880`) |
| a floor guard on the thermal arm | no | no | **yes**: `f > f_min` (`TPM:886`) |
| the response | a `while` loop: one step, `vTaskDelay(pdMS_TO_TICKS(DELTA_TEMP_UPDATE_PERIOD))`, re-read, repeat (`TPM:2166-2204`) | the same (`TPM:2316-2361`) | **one step per pass, no loop, no delay** (`TPM:894` → `:2182-2186`) |
| on leaving the thermal state | state → THERMAL_IDLE, a CRITICAL `Thermal idle state event` line, residency updated, and the clock sent to the **boot point** (`TPM:2216-2232`) | the same (`TPM:2366-2382`) | **there is nothing to leave**: no thermal state, no exit line, no boot-point reset |
| the step | fixed **50 MHz**, clamped to 300–700 MHz (`include/thermal_pwr_mgmt.h:56-58`; `TPM:1769-1811`) | one VMIN-LUT point | one VMIN-LUT point (100 MHz on this card) |
| the top of the range | 700 MHz — 800 is unreachable | the LUT's maximum | the LUT's maximum |
| the voltage | computed linearly from the boot point | from the VMIN LUT | from the VMIN LUT |
| APM off when the LUT is invalid | no check | yes (`TPM:1703-1723`) | yes (`TPM:1628-1648`) |
| a latch into the thermal state | yes | yes | **no** |

0.20.0's and 0.18.0's thermal behaviour was first written up at
[`../2026-09-28-dvfs2-aifoundry2/plan/review-governor.md`](../2026-09-28-dvfs2-aifoundry2/plan/review-governor.md)
(§0.2, §2.2, §5) when both cards were believed to run 0.20.0. Every line of theirs quoted above was re-read
first-hand for this report; the review's readings of those two revisions all hold. What does not hold is the
mapping from card to build, and that correction is already recorded at
[`../../../findings/14-card-behaviour.md:310-317`](../../../findings/14-card-behaviour.md).

## What firmware the two cards run

| | aifoundry2 (card 0) | aifoundry3 |
|---|---|---|
| last committed card read | **release 1.4.0, BL1 and BL2 0.22.0, PMIC 1.5.0, minions 0.25.1** — read fresh under E69's G0 gate, 27 Oct 2026 13:56–13:58 PDT, and re-reported at the E72 handoff ([`../2026-10-27-e72-600mhz/handoff-evidence.json`](../2026-10-27-e72-600mhz/handoff-evidence.json) `.firmware_at_handoff`; [`../../../findings/14-card-behaviour.md:310-312`](../../../findings/14-card-behaviour.md)) | **release 1.3.1, BL1 and BL2 0.20.0, PMIC 1.5.0, minions 0.23.0** — 25 Sep 2026 22:29:54, identical in all three passes ([`../2026-09-25-claims-v3/raw/aifoundry3/tel/p1/gov/fw.txt`](../2026-09-25-claims-v3/raw/aifoundry3/tel/p1/gov/fw.txt), and `p2`, `p3`) |
| how stale | 4 days | **36 days, and 🛑 not to be trusted**: aifoundry2 read 1.3.1 / 0.20.0 on the same day from the same harness and had moved to 1.4.0 / 0.22.0 by 27 Oct with no lab record of the change |
| the trap in the manifests | `et-lab-manifest`'s `et_soc1 version=` is the **host driver module's** version, not the card's. The newest committed aifoundry3 manifest reads `et_soc1 version=0.20.0 srcversion=…` at 27 Oct 14:38 PDT ([`../2026-10-27-e70-saturation-ladder/aifoundry3/hl/p796/manifest.txt`](../2026-10-27-e70-saturation-ladder/aifoundry3/hl/p796/manifest.txt)) — that is **not** evidence about its BL2 | same trap, same file |
| what the same manifest *does* fix | — | the boot pin: `clock guard … 600 400 0` (minion MHz, NoC MHz, TDP W), i.e. 600 MHz / 400 MHz NoC / **TDP 0 W** still set at that boot |

**So nothing committed says what BL2 aifoundry3 runs today.** The aifoundry3 lane of this workflow reads it on
the card (`DM_CMD_GET_MODULE_FIRMWARE_REVISIONS`); until that read lands, no 0.22.0 statement here may be
applied to aifoundry3, and no 0.20.0 statement either. The difference is not cosmetic for the E78/E79 ladders:
under 0.20.0 a TDP of 0 latches the governor dead the first time the mean passes 65 °C, so a 600 MHz pin is
safe and permanent; under 0.22.0 the same TDP is a *reversible* pin whose only guard above the floor is the
host harness ([`../../../findings/14-card-behaviour.md:333-347`](../../../findings/14-card-behaviour.md)).

## For the blog, in one paragraph

The ET-SoC-1's clock is set by two firmware tests, and they fail in different ways, so the same chip gives the
same work two different speeds depending on how long you run it. **In a burst, power decides and the clock
dithers.** The service processor compares a 1.3-second running average of the whole board's power with a 65 W
cap once every quarter of a second, and moves the minion clock one table point — 100 MHz — down if it is over
and one point up if it is under. There is no dead band, so the clock does not settle: it hunts. Feed it random
floating-point numbers and it climbs 600 → 700 → 800 MHz in two passes, touches 88 W, gets knocked back, and
climbs again — which is why a cool card runs random data about 25 % slower than zeros, and why the number you
measure depends on how many of those cycles your burst contains. **Run the same work for a minute and heat
takes over, and heat does not dither, it clamps.** Once the die is warm the firmware's *first* test fires: the
integer average of 34 on-die temperature sensors against a 65 °C threshold, strict, with no hysteresis at all.
Each time that average reads 66 the clock loses one point; every pass it reads 65 or less, the power test gets
a turn and gives one point back. The die ends up pinned *on* the threshold, which means the **board power** is
pinned too — at whatever draw heats this card's die to 65 °C, measured as 49.2 to 51.4 W. So the sustained
clock of any workload is simply the clock at which that workload draws 50 W. Multiplying zeros draws 36 W flat
out, never reaches the band, and keeps all 800 MHz. **Random `int8` draws 44 W at 600 MHz and 53 W at 800, so
the band falls inside the clock range and the governor parks it at 763 MHz — two thirds of its samples at
800 MHz, a third stepped down, 94 % of its flat-out speed.** Random `fp32` and `fp16` draw 54 W and 51 W
*already at 600 MHz* — their floor is hotter than the threshold. The firmware has no point left to give back,
so it stops stepping, stops logging, and, because the thermal test short-circuits the power test, never lets
the clock rise again: the clock sits at exactly 600 MHz while the die floats up to 67 °C. Those workloads keep
75 % of their flat-out speed, and the loss is not a power limit at all — the card is drawing only 54 W against
a 65 W cap. It is the one degree of hysteresis the firmware does not have. Raise that threshold five degrees
on a real card and the clamped cell goes from 763.4 MHz with eleven throttle events to a flat 800.0 MHz with
none; lower it and everything slows. The clock is a thermostat, and the kind of numbers you multiply is the
dial.

## Files

| Path | What |
|---|---|
| [`trace_tests.py`](trace_tests.py) | the eight predicates of §Results 8 run over the committed E64 and E69 run records; reads `event_list`, writes the JSON |
| [`trace-tests.json`](trace-tests.json) | its output: the predicate counts, plus a per-run row for all 76 runs |
| [`clamp_model.py`](clamp_model.py) | the constant-power clamp of §Results 9, on committed E64 numbers only; nothing is fitted |
| [`clamp-band.json`](clamp-band.json) | its output: the band, and the nine cells with their brackets and residuals |

```bash
cd docs/reports/data/2026-10-31-q130-governor-thermal-branch
python3 trace_tests.py --out trace-tests.json
python3 clamp_model.py --out clamp-band.json
```

## Departures, limits and what is not established

- **No pre-registration, because nothing was measured on a card.** This is a source read plus a re-reduction
  of committed data. The eight predicates were written from the source before the rings were counted, but they
  were not pushed first, so they are **checks, not registered predictions**. Called out rather than dressed up.
- **The build identity residual E69 recorded still stands**, and this report inherits it: the card exposes no
  BL2 git hash through any allowed query, so a source read establishes the behaviour of *a* 0.22.0. §Results 7
  narrows it from the other end — three signatures in the card's own trace strings and record layout rule out
  0.20.0 — but they cannot distinguish one 0.22.0 build from another.
- **T6 is untested** (§Results 8): no `Power idle state event` line of either form is in these rings, so the
  one signature that would be decided by the *level* of the idle line (CRITICAL with numbers at 0.20.0, INFO
  without at 0.22.0) is unmeasured here. A no-sampler run with a 30 s dump cadence would settle it.
- **The clamp model is in-sample** (§Results 9) and linear in frequency. E64-T1's out-of-sample 4.8–9.6 MHz is
  the accuracy number to quote; this one is a decomposition.
- **The FreeRTOS tick in SP time is not re-established here.** E64's own clock alignment gives the SP's
  *microsecond* timer as 999,809 and 988,451 Hz over the two sessions
  ([`../2026-10-23-e64-horace-power-limit/results.json`](../2026-10-23-e64-horace-power-limit/results.json)
  `.fits.s1.tick_hz`, `.fits.s2.tick_hz`), i.e. a true microsecond to within 0.02 % and 1.2 % — which answers
  the review's §12 question for *that* timer, not for `configTICK_RATE_HZ`. The 0.20.0 loop period of 0.40 s
  rests on the review's 401 µs/tick, which is unchanged and not re-derived.
- **The 0.16 s floor on the inter-decision gap** (T7) is the harness's sampler loading the SP, not the
  firmware's own pass. The firmware's sleep is 10 ms of nominal tick; the real pass is I2C-bound.
- **What the PMIC does with either alarm write is not established**, in either direction. Its firmware is
  closed and its system-temperature register reads 0 on every card the lab has measured.
- 🛑 **`tools/claims-v3/hpl/run_hpl.py:220-275`, the `--dry` simulator, still models 0.20.0's governor** — a
  thermal `while` loop, a `thermal_idle` exit to the boot point, and a `1.05 × TDP` power-down exit that does
  not exist in this card's build. It affects dry-run predictions only, never reduced data, but any Q130 cell
  that quotes a `--dry` number is quoting the wrong mechanism.

## What this changes

- **For the blog:** the paragraph above, and §Results 9's table, which turns "heat limits the clock" into one
  number — a 49.2–51.4 W board-power band — that every format × kind cell can be placed against.
- **For the Horace hub, Status item 7** ("the governor's thermal branch at the build the card runs"): closed as
  a source read with card checks, with T6 named as the one untested signature and the build-identity residual
  carried over from E69.
- **For the Levels tab, stop 1:** the trip is no longer a free parameter swept over {65.5, 66.0} °C by
  convention — it is a strict integer `>` on a truncated 34-sensor mean (`@22:TPM:884`,
  `@22:driver/pvt_controller.c:577`), so the band *is* 65 to 66 and its width is worth 2.13 W of board power.
  E64-T1 should quote that as its reason rather than as a sweep.
- **For `docs/findings/14-card-behaviour.md`:** § "The clock governor is thermal first" can now cite the
  build the card runs for the thermal half, and § "The governor's two knobs" gains §Results 5 (the thermal arm
  is byte-identical 0.21.0 → 0.22.0, so SW-22147 cannot reach it) and §Results 7 (the E64 rings date the
  card's 0.22.0 to 23 Oct). § "The clock governor, by firmware build" needs a 0.22.0 column that says
  *no loop, no latch, no thermal state*.
- **For the next card session:** read each card's own `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS` and commit it.
  aifoundry3's committed firmware is 36 days old and was taken on the day aifoundry2's identical-looking read
  turned out to be about to change.
