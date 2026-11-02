# Q130(d) — the governor's thermal branch, read at the build aifoundry2 runs (BL2 0.22.0)

Sat 31 Oct 2026 (week 44). **Desk only: no card was opened, claimed or set for this.** A source read of the
firmware arm that turns heat into clock, at the revision that matches the build aifoundry2's card reports,
with every statement checked against the service-processor traces E64 and E69 already committed.

**What is new here, stated narrowly.** The lab record already carries a 0.22.0 thermal column:
[`../../../findings/14-card-behaviour.md:223-231`](../../../findings/14-card-behaviour.md) has a `353f20e`
(= `836a4ab`) column — "it is the 0.22.0 snapshot", as that file says at `:316-317` — with rows for when the
thermal test acts, "one table point down per pass", "Hysteresis: none", the 600/700/800 VMIN points and the
75 °C/75 W alarm → 300 MHz safe state; `:230` already records that at a 65 °C threshold the entry line prints
66 (E51, 20 of 20). What this report adds is: the arm **read line by line** for the first time at that build
(the `else if` chain and what it does at the floor, the integer truncation, what does *not* latch, the two
unused hysteresis macros); the arm **dated to the card** by the E64 rings, four days before E69 read the
version string; the **0.21.0 → 0.22.0 diff** that retires Q129's wrap-hazard argument; and the clamp expressed
as a **band of board power**, which is what the blog's kinds-of-numbers column needs. The only other
first-hand write-up of the thermal arm is at 0.20.0, in
[`../2026-09-28-dvfs2-aifoundry2/plan/review-governor.md`](../2026-09-28-dvfs2-aifoundry2/plan/review-governor.md),
a build this card turned out not to be running; everything the lab has written at 0.22.0 until now was about
the **power** arm (the throttle-wrap gate
[`../2026-10-27-q129-throttle-wrap-gate/`](../2026-10-27-q129-throttle-wrap-gate/README.md), the two set
paths, E72's TDP pin).

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

3. **The thermal arm wins the pass even when it cannot act, and that is what the 600 MHz clamp is — but the
   floor is a ratchet with a near-zero duty cycle, not silence.** The inner guard
   `minion_curr_frequency > minion_min_frequency` (`@22:TPM:886`) stops the step at the VMIN floor, while the
   *outer* test has already claimed the `else if` chain — so **on a pass whose mean reads above the threshold**
   the power arm never runs and cannot lift the clock, and nothing is logged. The mean, however, dithers across
   one integer degree, so some passes read at or below the trip, the chain falls through, and the power arm
   does lift the clock one point. In the committed rings that happens **199 times with the clock at 600 MHz,
   and all 199 next records read 700 MHz** — the clock really rose — of which **53 were undone by a thermal
   step before any other decision**, the 700 MHz excursion lasting 0.17–0.23 s (median **0.19 s**, one
   management pass) ([`trace-tests.json`](trace-tests.json) `.T9_power_up_logged_at_the_floor`). So the floor
   is a 600↔700 limit cycle whose duty cycle is near zero, and the clamp is the *absence of a sustained*
   up-step, not the absence of any. 🛑 The report's first version said "nothing is logged" and "never lets the
   clock rise again" flatly; that was wrong, and T9 (§Results 8) is the test that catches it.

   How near zero depends on how far over the band the cell's floor power sits:
   - **fp32/randn** (54.27 W at 600 MHz, 2.91 W over the band's top — 4.5 × the die line's own uncertainty):
     **exactly 600 MHz in every one of the last twenty 2 s bins**, and its ring holds **no governor decision
     of any kind after t = 24.65 s**. Here the silence is real.
   - **fp16/randn** (51.47 W, only **0.11 W** over the top — inside the die line's ±0.65 W, so the band
     arithmetic does not decide this cell's regime at all): sustained mean **600.5 MHz**, 600 in every
     sustained bin but one (611.1 MHz at t = 50 s), with three floor power-ups inside the sustained window.
     A cell sitting *on* the band's top edge is exactly what that looks like.

   Both figures are measured ([`../2026-10-23-e64-horace-power-limit/README.md:91,94`](../2026-10-23-e64-horace-power-limit/README.md),
   `results.json` `.runs[SUS-02-fp32-randn-1024-r1|SUS-05-fp16-randn-1024-r1].sus_bins`). ⚠ **Neither cell had
   reached equilibrium:** across the sustained window fp32/randn's die climbs 66 → 68 °C (`die_end` =
   `die_max` = 68) and its board power 54.07 → 54.90 W, and fp16/randn ends at 67 °C. So "die 67.1 °C, 54.4 W"
   and "66.1 °C, 51.3 W" are means over a rise — **lower bounds**, which only strengthens the point that this
   is not a power limit.

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
   version string.** Four independent signatures, over 76 runs and 3,001 parsed ring entries (1,040 `New OP:` lines, 1,033 power-status records, 542 power-ups, 224 power-downs, 162 thermal steps — i.e. **928 CRITICAL governor lines**)
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
   - **98 power-status records carry `throttle_state = 0`** — POWER_IDLE at 0.22.0's enum — so master-minion
     idle transitions really happened during these runs (the census of all 1,033 is `{0: 98, 1: 545, 2: 390}`,
     [`trace-tests.json`](trace-tests.json) `.pstat_throttle_state_census`). At 0.20.0 each of those also
     writes a **CRITICAL** `Power idle state event, current pwr %u  tdp level %u` line (`@20:TPM:853-855`); at
     0.22.0 the line is `LOG_LEVEL_INFO` with **no arguments** (`@22:TPM:3117`). These rings carry all 928
     CRITICAL governor lines and **not one** numbered idle line. That is the fourth signature, and it is the
     half of T6 that the rings *can* decide.

8. **Every predicate the source read implies holds on the card — once T9 is added and T8's denominator is
   written out.** From the same 76 runs:

   | # | what the source says | where | what the rings show | verdict |
   |---|---|---|---|---|
   | T1 | the test is strict `>` on integers, so the first tripping reading is `thr + 1` | `@22:TPM:884` | at threshold 65 the printed temperature is **66** (151) or 67 (3); at threshold 62 it is **63** (8). **Never equal to the threshold, never below it** | PASS |
   | T2 | a thermal step is exactly one VMIN point | `@22:TPM:1888-1906`, `driver/flashfs.c:2384-2399` | **161 of the 162** thermal steps have a measurable from→to, and all 161 are exactly one point: **800→700** (79) and **700→600** (82). No 800→600, no sub-600 target. The 162nd is a *stale* ring entry in `HOT-03-fp32-zeros-edge63-r1`, its record timestamped t = −45.2 s, before that run's own timebase, with no earlier operating point in the ring to form a pair from (`.T2_thermal_steps_without_a_from_to`) | PASS on 161/162 |
   | T3 | no step at the floor | `@22:TPM:886` | **0 of 162** thermal steps taken while the clock was already 600 MHz | PASS |
   | T4 | the step is requested as POWER_DOWN | `@22:TPM:894` | state 2 after 162/162 thermal steps; state 2 after 224/224 power-downs; state 1 after 542/542 power-ups | PASS |
   | T5 | no thermal loop, so no thermal-idle line | 0.22.0 has no `thermal_throttling()` | 0 such lines | PASS |
   | T6 | the idle line carries no numbers at 0.22.0 (INFO) | `@22:TPM:3117` vs `@20:TPM:853-855` | **no `Power idle state event` line of either form is in these rings.** Both forms are genuinely tested: the committed parser holds the numbered 0.20.0 pattern at `tools/claims-v3/dv2/sptrace_events.py:46` **and a bare `Power idle state event` pattern at `:47`**, and `hpl/sptrace_full.py:77-85` emits a bare match with no `pwr_mw`, so a 0.22.0 INFO line would land in `T6_power_idle_without_numbers`. Both counts are 0 | UNTESTED — the 4 KB ring holds under a second at INFO with a sampler, and the harness dumps during work. But see §Results 7's fourth signature: the 98 state-0 records show the idle transitions happened, with no numbered CRITICAL line, which settles the 0.20.0 half |
   | T7 | the arm can act at most once per dm pass | `rtos_task/dm_task.c:267,275` | successive governor decisions are **≥ 0.16 s** apart, median 0.21 s (n 852); consecutive thermal steps ≥ 0.20 s, median 0.46 s (n 143). A step lands 0.02–0.14 s after its own line, median 0.05, p95 0.09 (n 928, `.T7_seconds_decision_to_record`) | PASS |
   | T8 | the ratchet: thermal gives one point back per trip, power takes one back per pass | `@22:TPM:884-920` | of the 162 thermal steps, **159 have a following decision: 132 a power-up, 27 another thermal step, and 0 a power-down.** The zero is the content — a thermal step is never followed by a power-down | PASS |
   | **T9** | at the floor the chain swallows the pass **only while the mean reads above the trip**, so a pass that reads at or below it reaches the power arm and lifts the clock one point | `@22:TPM:884-896` vs `:898-920` | **199 power-ups are logged with the clock at 600 MHz, and all 199 next records read 700 MHz**; 53 of them are undone by a thermal step before any other decision, the excursion lasting 0.17–0.23 s (median 0.19). The floor is a 600↔700 limit cycle with a near-zero duty cycle | PASS — **added 31 Oct after it refuted §Results 3's first wording** |

9. **The sustained clamp is a constant-POWER clamp at 49.2 ± 0.7 to 51.4 ± 0.7 W of board power — an
   E64-session quantity, not a card constant — and that one band places the whole kinds-of-numbers column**
   ([`clamp-band.json`](clamp-band.json), [`clamp_model.py`](clamp_model.py)). Because the arm is bang-bang on
   the integer mean, the steady state puts the die *on* the trip, so the board power sits where E64's own
   thermal line puts the trip: `board_W = (trip_C − 41.88) / 0.4696`
   ([`../2026-10-23-e64-horace-power-limit/surface.txt:27`](../2026-10-23-e64-horace-power-limit/surface.txt)).
   The trip is a band in whole degrees — 65 is the last reading that passes, 66 the first that trips — so the
   clamp is **49.23 W to 51.36 W**, 2.13 W wide. Each kind then gets whatever clock puts *its* power in that
   band:

   | type/kind | board W at 600 | at 800 | sustained W | in band? | die °C | sustained MHz | share at 800 | modelled clock | regime (margin to the nearer edge) |
   |---|---:|---:|---:|:--:|---:|---:|---:|---|---|
   | fp32/zeros | 27.0 | 36.4 | 36.4 | no | 59.0 | 800 | 1.00 | 800 | never trips (12.8 W under) |
   | fp16/zeros | 27.4 | 36.4 | 36.1 | no | 59.0 | 794 | 0.97 | 800 | never trips (12.8 W under) |
   | int8/zeros | 27.9 | 37.6 | 37.6 | no | 59.0 | 800 | 1.00 | 800 | never trips (11.6 W under) |
   | int8/ones | 29.9 | 41.7 | 41.8 | no | 61.7 | 800 | 1.00 | 800 | never trips (7.5 W under) |
   | fp16/ones | 45.4 | 54.6 | **49.28** | **yes** | 65.4 | **737** | 0.48 | 684–730 | in the clamp |
   | fp32/ones | 45.2 | 54.4 | **49.38** | **yes** | 65.4 | **738** | 0.48 | 688–734 | in the clamp |
   | int8/randn | 44.4 | 53.2 | **50.67** | **yes** | 65.3 | **763** | 0.66 | 710–759 | in the clamp |
   | fp16/randn | 51.5 | 63.9 | 51.34 | yes | 66.1 | **600.5** | 0.00 | 600 | floor over the band by **0.11 W** — ⚠ inside the ±0.65 W, so the band does **not** decide this cell |
   | fp32/randn | 54.3 | 67.8 | 54.36 | no | 67.1 | **600** | 0.00 | 600 | floor over the band by 2.91 W (4.5 × the uncertainty) |

   The claim has a **power form** and a **clock form**, and they are not equally good:

   - **Power form (the one to quote).** For each thermally clamped cell the *measured* sustained board power
     lies in the band: 49.28, 49.38 and 50.67 W for the three discriminating cells — **3 of 3 inside**
     49.23–51.36 (and fp16/randn's 51.34 W, the marginal cell, inside too).
   - **Clock form (modelled, and biased).** The bracket is each cell's own power curve read linearly in *f*
     between its measured 600 and 800 MHz points. The measured clock lands **above the bracket's top in 3 of
     3** discriminating cells — +6.6, +4.4, +4.3 MHz, mean **+5.1** — which is the sign a linear-in-*f*
     interpolation **must** produce under a convex *P(f)*: voltage rises with frequency too. So that is a
     **one-sided bias by construction, not an rms error**, and the earlier wording ("rms 3.6 MHz over nine
     cells, 5.2 over three") dressed a bias as a spread. fp16/zeros' −6.0 MHz is not part of it: that cell
     never trips (thermal share 0.00) and its 794 MHz mean is E64's own **ramp** share of 0.03
     ([`../2026-10-23-e64-horace-power-limit/README.md:92`](../2026-10-23-e64-horace-power-limit/README.md)).

   🛑 **Two bounds on the band, both now computed in [`clamp-band.json`](clamp-band.json):**

   - **Within E64.** The die line is a fit. Its residuals over E64's own nine sustained points are
     +0.05, +0.17, −0.52, +0.21, +0.38, +0.33, −0.37, +0.11, −0.31 °C: **rms 0.306 °C = 0.65 W** per band
     edge, max 0.52 °C = **1.10 W**, against a band only 2.13 W wide. Hence "49.2 ± 0.7 to 51.4 ± 0.7 W", and
     hence fp16/randn's regime being undecided by arithmetic (`.rows[].regime_decided_within_uncertainty`).
   - **Across sessions.** E69's **registered drift check FAILED**
     ([`../2026-10-27-e69-governor-knob/README.md:101-118`](../2026-10-27-e69-governor-knob/README.md)): the
     same cell (fp32 sustained `ones`, TDP 65 / thr 65) read 49.38 W at 65.4 °C on 23 Oct and **51.89 W at
     65.2 °C** on 27 Oct — **+2.51 W at the same die temperature**, more than the band's whole width, and
     51.89 W sits **above** this band's 51.36 W top. Against E69's four SUS cells E64's line is off by −1.05,
     −3.37, −5.15 and −4.14 °C (−2.2 to −11.0 W), all in the same direction. E69 reads it as a thermal-path
     change, not a governor change. **So this band is an E64-session quantity (23 Oct, aifoundry2), not a
     property of the card**, and the "at a 70 °C trip the band moves to 59.9–62.0 W" step below uses an
     intercept that demonstrably moved — which is why the *outcome* claim rests on E69's direct measurement
     instead (§Results 10).

   And it is **in-sample by construction and linear in frequency**: each cell's bracket uses that same run's
   own median board power at 600 and at 800 MHz. It is a *decomposition* — it says the clamp is a power clamp
   at the trip and that the trip's integer width is worth 2.1 W — next to which E64-T1's **out-of-sample**
   4.8–9.6 MHz
   ([`../2026-10-27-q129-governor-temperature/README.md:76-87`](../2026-10-27-q129-governor-temperature/README.md),
   which counts five discriminating cells where this table counts three) is the honest accuracy number. The
   two agree on the mechanism: T1's two free parameters are γ and **the trip**, and it sweeps the trip over
   exactly {65.5, 66.0} °C because of the integer truncation this read pins to `@22:driver/pvt_controller.c:577`.

10. **E69 is the experiment that moved the threshold, and the clamp moved with it — on two of its four cells,
    and the other two are named here too.** All four of E69's sustained cells
    ([`../2026-10-27-e69-governor-knob/README.md:63-79`](../2026-10-27-e69-governor-knob/README.md), all
    fp32 `ones`, 27 Oct), with **E69's own verdict** on each:

    | TDP | thr | measured MHz | die °C | board W | thermal / power steps | share at 800 | E69's verdict | does it support this read? |
    |---:|---:|---:|---:|---:|---|---:|---|---|
    | 65 | 65 | 763.4 | **65.2** | 51.89 | **11** / 0 | 0.66 | the control; its **drift check vs E64 FAILED** (+25.5 MHz, +2.51 W) | **yes** on the mechanism (die pinned at 65 °C in all twenty bins, 11 thermal steps); and it is the transfer bound of §Results 9 — its 51.89 W is *above* E64's band top |
    | 65 | **70** | **800.0** | 64.2 | 54.71 | **0** / 0 | **1.00** | a **ceiling artefact** on the number (800 is the top VMIN point); the step count and the 800-share are the content | **yes**, and this is the load-bearing cell: the clamp vanishes, measured directly, no band arithmetic needed |
    | 65 | **62** | 790.3 | 61.2 | 52.11 | 8 / 0 | 0.93 | **"Reported as inconclusive, not as a result"**: it gated at a 50 °C die, its last-40 s bins show the die still **climbing 59 → 62 °C**, and it never equilibrated against its own threshold inside 76 s. Registered 649.8, a 140 MHz miss | **no — it is not a test.** Its die mean (61.2 °C) is *below* its own 62 °C threshold, so "the steady state puts the die on the trip" did not hold there, exactly as a non-equilibrated run would look. This report uses only its *event* lines (T1's 62 bucket: 8 steps, all printing 63) |
    | **50** | 65 | 769.6 | 61.2 | 49.95 | 0 / **11** | 0.70 | its **speed prediction is refuted by 70 MHz** (registered 700.0); the limiter switched from heat to power | **partly**: the *cause flip* is exactly this read's `else if` chain — with the die under the trip, the power arm gets the pass and logs 11 power steps — but the *speed* is a model failure E69 owns |

    So: raising the threshold five degrees takes the same work from 763.4 MHz with eleven throttle-downs to a
    flat 800.0 MHz with none, which is what "the sustained gap is 36.6 MHz and it belongs to the threshold"
    means mechanically. The band at a 70 °C trip computes to 59.9–62.0 W, above this cell's 54.4 W at 800 MHz
    — but after E69's failed drift check that arithmetic is corroboration, not evidence: **the clamp's
    disappearance is measured, as 0 thermal steps and a share at 800 of 1.00.**

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

- **Thermal has priority on the passes it claims, including the priority to do nothing.** On a pass where the
  mean reads above the trip with the clock already at the floor, branch 1 is taken, its inner guard fails, and
  branches 2 and 3 never run: the clock is held at 600 MHz by the *absence* of an up-step, not by a down-step.
  That priority is **per pass, not permanent** — the mean dithers across the trip, so a pass reading 65
  falls through to branch 3 and does lift the clock (T9: 199 power-ups logged at 600 MHz, all 199 followed by
  a record reading 700, 53 undone by the next trip within 0.19 s). What the clamp costs is the *sustained*
  up-step: in E64's two floor-pinned cells the share of samples at 800 MHz is exactly 0.00 and the thermal
  share 1.00, with 700 MHz holding 0.077 and 0.133 of the whole run and essentially none of the sustained
  window ([`../2026-10-23-e64-horace-power-limit/README.md:91,94`](../2026-10-23-e64-horace-power-limit/README.md),
  [`trace-tests.json`](trace-tests.json) `.per_run`).
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
  the power arm takes one back on *every* pass where the mean is at or below the threshold. In the rings, of
  the 162 thermal steps **159 have a following decision: 132 a power-up, 27 another thermal step, 0 a
  power-down** — the zero is the content. `power_up → power_up` runs 184 times, so the two-pass climb
  600→700→800 the review first saw at 0.20.0 survives here, but as two ordinary passes rather than one loop.
  The sustained mean clock is then the duty cycle of that ratchet, which is why `int8/randn` reads 763 MHz
  with 0.66 of its samples at 800 and `fp32/ones` reads 738 MHz with 0.48 — and why `fp16/randn`, at the
  floor, reads 600.5 MHz: the same ratchet with a duty cycle of about half a percent.

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

*Dated note, Mon 2 Nov 2026 (week 45), added by Q134's records after their verification, without editing the text above:
the read this paragraph and the last bullet of "What this changes" ask for, `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS`, is a
PMIC command. At et-platform `836a4ab` its handler writes the PMIC's firmware-management command register twice,
ACTIVE_SLOT then VERSION, and reads the data register after each (the chain is in [E114's
README](../2026-11-01-e114-card0-replicates/README.md), C1); by the lab's standard since
[E85](../2026-10-31-e85-camera-kinds/README.md)'s correction C1, a DM command the service processor passes to the PMIC is
a PMIC command. The read was made: E79 sent it on aifoundry3 at 09:27:22 PDT on 31 October, three minutes before this
README was first committed
([`../2026-10-31-e79-fp16-int8-bit-prices/ident/firmware.txt`](../2026-10-31-e79-fp16-int8-bit-prices/ident/firmware.txt)),
and E82 and E84 sent it on aifoundry1's two cards that afternoon, all under Q130's rule of no PMIC work. Take a card's
identity from its last committed revisions read and its module uptime (`DM_CMD_GET_MODULE_UPTIME`, service-processor RAM):
an image takes effect only through a reset, so an uptime longer than the time since that read carries the identity, as
E77, E118 and E120 took it. Send the query again only with the owner's and the firmware maintainer's authorization.
[05-claims.md](../../../findings/05-claims.md), "Q134", lists every run that sent it.*

## For the blog, in one paragraph

The ET-SoC-1's clock is set by two firmware tests, and they fail in different ways, so the same chip gives the
same work two different speeds depending on how long you run it. **In a burst, power decides and the clock
dithers.** The service processor compares a 1.3-second running average of the whole board's power with a 65 W
cap about once every fifth of a second — 133 ms when nothing else is asking the processor questions, 0.24 s as
E64's own runs fit it with a sampler polling — and moves the minion clock one table point — 100 MHz — down if
it is over and one point up if it is under. There is no dead band, so the clock does not settle: it hunts. Feed it random
floating-point numbers and it climbs 600 → 700 → 800 MHz in two passes, touches 88 W, gets knocked back, and
climbs again — which is why a cool card runs random data about 25 % slower than zeros, and why the number you
measure depends on how many of those cycles your burst contains. **Run the same work for a minute and heat
takes over, and heat does not dither, it clamps.** Once the die is warm the firmware's *first* test fires: the
integer average of 34 on-die temperature sensors against a 65 °C threshold, strict, with no hysteresis at all.
Each time that average reads 66 the clock loses one point; every pass it reads 65 or less, the power test gets
a turn and gives one point back. The die ends up pinned *on* the threshold, which means the **board power** is
pinned too — at whatever draw heats this card's die to 65 °C, which on the day this was measured was
49.2 to 51.4 W, each edge good to about ±0.7 W. So the sustained clock of any workload is simply the clock at
which that workload draws about 50 W. Multiplying zeros draws 36 W flat out, never reaches the band, and keeps
all 800 MHz (794 in one of the three zeros cells, and those 6 MHz are the run's own warm-up, not a throttle).
**Random `int8` draws 44 W at 600 MHz and 53 W at 800, so the band falls inside the clock range and the
governor parks it at 763 MHz — two thirds of its samples at 800 MHz, a third stepped down, 94 % of its
flat-out speed.** Random `fp32` and `fp16` draw 54 W and 51 W *already at 600 MHz* — their floor is hotter than
the threshold, and the firmware has no point left to give back. What is left is a stalemate on a single
integer: the degree-resolution average wobbles across the trip, so most passes are claimed by the heat test
and do nothing, and the occasional pass that reads 65 lets the power test lift the clock to 700 MHz for about
a fifth of a second before the next reading of 66 takes it back. Averaged over a minute that is 600.0 and
600.5 MHz — a clock pinned at the floor by the *absence of a lasting* up-step — while the die floats up to
67–68 °C and is still climbing when the run ends. Those workloads keep 75 % of their flat-out speed, and the
loss is not a power limit at all: the card is drawing only 54 W against a 65 W cap. It is the one degree of
hysteresis the firmware does not have. Raise that threshold five degrees on a real card and the clamped cell
goes from 763.4 MHz with eleven throttle events to a flat 800.0 MHz with none; lower it and everything slows.
The clock is a thermostat, and the kind of numbers you multiply is the dial.

## Files

| Path | What |
|---|---|
| [`trace_tests.py`](trace_tests.py) | the **nine** predicates of §Results 8 run over the committed E64 and E69 run records; reads `event_list`, writes the JSON. T9 and the `pstat` state census were added 31 Oct after the verifier's pass |
| [`trace-tests.json`](trace-tests.json) | its output: the predicate counts (`.T9_power_up_logged_at_the_floor`, `.T8_after_a_thermal_step`, `.T7_seconds_decision_to_record`, `.T2_thermal_steps_without_a_from_to`, `.pstat_throttle_state_census`), plus a per-run row for all 76 runs with its floor power-up counts |
| [`clamp_model.py`](clamp_model.py) | the constant-power clamp of §Results 9, on committed E64/E69 numbers only; nothing is fitted. Now also computes the band's own uncertainty and E69's transfer bound |
| [`clamp-band.json`](clamp-band.json) | its output: the band with `±` per edge (`.clamp_band_board_W`, `.die_line_uncertainty`), E69's failed-drift transfer bound (`.transfer_bound_E69`), the power form vs the clock form (`.agreement`), and the nine cells with their regime margins |

```bash
cd docs/reports/data/2026-10-31-q130-governor-thermal-branch
python3 trace_tests.py --out trace-tests.json
python3 clamp_model.py --out clamp-band.json
```

## Departures, limits and what is not established

- 🛑 **One wrong reading of the source, found by this workflow's verifier and corrected here (31 Oct).** The
  first version of §Results 3, the headline, the `for_integration` line and the blog paragraph all said that at
  the VMIN floor the thermal arm swallows the pass so the power arm "never runs and cannot lift the clock",
  that "nothing is logged" and that it "never lets the clock rise again". The same committed rings it cited
  refute that: 199 power-ups are logged with the clock at 600 MHz and **all 199** next records read 700 MHz, 53
  of them undone by a thermal step within 0.19 s, including 11 and 10 in the two floor-pinned SUS cells
  themselves. The source text is right pass by pass; the *absolute* reading of it was not, because the mean
  dithers across the one integer degree the test uses. T9 was added as the predicate that catches it, and the
  claim is now "the absence of a *sustained* up-step". Silence is true only of the deeply-over-trip cell
  (`fp32/randn`, no decision at all after t = 24.65 s). The report's own T8 figure (`thermal_down → power_up`
  132) *was* this ratchet and the contradiction went unnoticed for one commit.
- **No pre-registration, because nothing was measured on a card.** This is a source read plus a re-reduction
  of committed data. The predicates were written from the source before the rings were counted, but they
  were not pushed first, so they are **checks, not registered predictions** — and T9, the ninth, was written
  *after* the rings refuted a claim, which makes it the weakest kind of check there is. Called out rather than
  dressed up.
- **Not new to the lab record, and said so in the header:** `docs/findings/14-card-behaviour.md:223-231`
  already carries a 0.22.0 thermal column (`353f20e` = `836a4ab`), including "one table point down per pass",
  "Hysteresis: none" and, at `:230`, the prints-66-at-a-65-threshold fact (E51, 20 of 20). The first version
  said "the thermal arm was last read at 0.20.0" and asked for a 0.22.0 column to be *added*; both are
  corrected.
- **The band's uncertainty and its session scope** (§Results 9): ±0.65 W per edge from the die line's own
  residuals (max 1.10 W) against a 2.13 W band, and E69's **failed** registered drift check (+2.51 W at the
  same die temperature, 51.89 W above the band's top; four cells off by −2.2 to −11.0 W) as the cross-session
  transfer bound. The band is an E64-session quantity. The first version quoted it to 0.01 W with no interval.
- **The clock bracket's error is one-sided** (§Results 9): measured above the bracket top in 3 of 3
  discriminating cells, mean +5.1 MHz, as a linear-in-*f* interpolation under a convex *P(f)* must be. The
  first version reported it as an rms over nine cells, which hid the bias and folded in a cell (fp16/zeros)
  that never trips.
- **The two floor-pinned cells had not equilibrated:** `fp32/randn`'s die climbs 66 → 68 °C over the sustained
  window and its power 54.07 → 54.90 W; `fp16/randn` ends at 67 °C. The 67 °C and 54 W figures are therefore
  **lower bounds**, which strengthens rather than weakens the "not a power limit" point.
- **E69's other two sustained cells are now listed** (§Results 10) with E69's own verdicts: thr62 is
  *inconclusive by E69's own judgement* (die still climbing 59 → 62 °C, never equilibrated, 140 MHz miss) and
  tdp50's speed prediction is *refuted by 70 MHz*. The first version quoted only the two rows that agreed,
  while using thr62's event lines for T1's 62 bucket.
- **The build identity residual E69 recorded still stands**, and this report inherits it: the card exposes no
  BL2 git hash through any allowed query, so a source read establishes the behaviour of *a* 0.22.0. §Results 7
  narrows it from the other end — three signatures in the card's own trace strings and record layout rule out
  0.20.0 — but they cannot distinguish one 0.22.0 build from another.
- **T6 is untested** (§Results 8): no `Power idle state event` line of either form is in these rings, so the
  one signature that would be decided by the *level* of the idle line (CRITICAL with numbers at 0.20.0, INFO
  without at 0.22.0) is unmeasured here. It is a real test rather than dead code — the committed parser holds
  **both** patterns, the numbered one at `tools/claims-v3/dv2/sptrace_events.py:46` and a bare
  `Power idle state event` at `:47`, and `hpl/sptrace_full.py:77-85` emits a bare match with no `pwr_mw` — and
  both counts are zero. A no-sampler run with a 30 s dump cadence would settle it. What the rings *do* settle
  is the 0.20.0 half, as §Results 7's fourth signature: 98 state-0 records, so the idle transitions happened,
  with no numbered CRITICAL line among the 928 CRITICAL governor lines present.
- **The clamp model is in-sample** (§Results 9) and linear in frequency. E64-T1's out-of-sample 4.8–9.6 MHz is
  the accuracy number to quote; this one is a decomposition. (Q129 counts five discriminating cells there,
  this table three.)
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
- 🛑 **`tools/claims-v3/hpl/run_hpl.py:218-278`, the `--dry` simulator, still models 0.20.0's governor** — a
  **sticky thermal state** (`:254`) with a `thermal_idle` exit that resets the operating point to the boot
  point (`:257-260`), and a `1.05 × TDP` power-down exit (`:271`, i.e. 68.25 W at a 65 W cap) that does not
  exist in this card's build. Its own docstring says "the 0.20.0 governor as the lab reads it". (Its `while`
  loops are in the *power* branches, `:269` and `:276`, not the thermal one; the first version of this report
  called the thermal path "a thermal `while` loop", which it is not.) It affects dry-run predictions only,
  never reduced data, but any Q130 cell that quotes a `--dry` number is quoting the wrong mechanism.

## What this changes

- **For the blog:** the paragraph above, and §Results 9's table, which turns "heat limits the clock" into one
  number — a 49.2 ± 0.7 to 51.4 ± 0.7 W board-power band, on the day it was measured — that every
  format × kind cell can be placed against. Quote the **power** form (3 of 3 clamped cells' measured sustained
  board power inside the band), not the modelled clock bracket.
- **For the Horace hub, Status item 7** ("the governor's thermal branch at the build the card runs"): closed as
  a source read with card checks, with T6 named as the one untested signature and the build-identity residual
  carried over from E69.
- **For the Levels tab, stop 1:** the trip is no longer a free parameter swept over {65.5, 66.0} °C by
  convention — it is a strict integer `>` on a truncated 34-sensor mean (`@22:TPM:884`,
  `@22:driver/pvt_controller.c:577`), so the band *is* 65 to 66 and its width is worth 2.13 W of board power
  (each edge ±0.7 W, E64-session). E64-T1 should quote that as its reason rather than as a sweep.
- **For `docs/findings/14-card-behaviour.md`:** § "The clock governor is thermal first" can now cite the
  build the card runs for the thermal half, and § "The governor's two knobs" gains §Results 5 (the thermal arm
  is byte-identical 0.21.0 → 0.22.0, so SW-22147 cannot reach it) and §Results 7 (the E64 rings date the
  card's 0.22.0 to 23 Oct, with four signatures). § "The clock governor, by firmware build" **already has the
  0.22.0 column** — `353f20e` (= `836a4ab`), as `:316-317` states — so what it needs is to be **relabelled
  "BL2 0.22.0 (`836a4ab`)"** and to gain the rows this read establishes: *no thermal loop, no latch, no
  thermal state in SP RAM*, and *at the floor the pass is swallowed only while the mean reads above the trip*.
- **For the next card session:** read each card's own `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS` and commit it.
  aifoundry3's committed firmware is 36 days old and was taken on the day aifoundry2's identical-looking read
  turned out to be about to change.
  *Dated note, Mon 2 Nov 2026 (week 45), added by Q134's records after their verification, without editing the text above:
  that query is a PMIC command, and E79, E82 and E84 sent it on 31 October; see the dated note under "What firmware the
  two cards run".*
