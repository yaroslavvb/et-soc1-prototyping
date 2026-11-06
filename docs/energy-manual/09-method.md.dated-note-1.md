# Dated note 1 beside 09-method.md (Fri 6 Nov 2026, week 45, about 03:05 PST): what the board meter is, from the public firmware

*This note sits beside [`09-method.md`](09-method.md) § "How a number in this manual was made", item 1 ("Board power is the PMIC's
reading through the management interface …"), and changes nothing in it; that file stays as committed (`39836c77`). It gives public
facts only: the public PMIC and service-processor firmware, and the lab's own committed measurements. It is MAP step 6's meter note
of the Q145 stock-take, owed since round A, written by Q145(b). Desk only; no card was touched.*

## Builds on

- **Checked:** the prior-work inventory, read Fri 6 Nov 2026 about 02:10 PST. Public rows read: P01, P03, P11, L11, L22, H07, H24,
  H28. The ids are opaque pointers into a private inventory.
- **Used:**
  - the public PMIC firmware, `aifoundry-org/et-boards` at `e5e0cf2` (runtime 1.7.0);
  - the public service-processor firmware, `aifoundry-org/et-platform` at `836a4ab60`;
  - E58 ([`2026-09-29-tau-aifoundry3/`](../reports/data/2026-09-29-tau-aifoundry3/README.md); `05-claims.md` lines 770-773;
    `03-experiments.md` lines 2274-2280);
  - E64 ([`2026-10-23-e64-horace-power-limit/README.md`](../reports/data/2026-10-23-e64-horace-power-limit/README.md) line 103);
  - the anatomy's card comparison
    ([`2026-11-05-q145a-anatomy-top-lines/README.md`](../reports/data/2026-11-05-q145a-anatomy-top-lines/README.md) lines 156-162,
    `538c98ce`);
  - the cards' PMIC versions as the lab read them: aifoundry2 1.5.0 (E69's README lines 199 and 210); aifoundry3 1.5.0 (Q130's
    governor-thermal-branch README line 335); aifoundry1's card 1 1.3.0 (E82's README line 326); card 0 1.6.1 (E84's README
    lines 172 and 239).
- **Not used:**
  - the ET-PCIe-Dev-Card-V3 schematic's sense network (R406), which would bound one board's meter tolerance. That read is owed
    (MAP row 16).
  - E82's protocol confound between card 1's September and October scales (its README lines 20-31 and 405-412: "only a
    same-protocol re-run would show whether card 1 changed"). This note does not settle it.
- **Tiers:** public only.

## 1. One fixed board-meter gain for every board

In the public PMIC firmware the board's power is the 12 V hot-swap current times the 12 V voltage:
- The current is the LTC4218's IMON output: a 1 mΩ sense resistor, 6.67 µA/mV and a 12.4 kΩ load
  (`firmware/et-soc1-pmic/common/HardwarePlatform/Drivers/inc/adc.h` lines 24-26).
- It is divided by **one fixed `CUR_ADJ_FACTOR` of 1.0787** (line 27): "fudge factor due to PCB resistance near R406 (PCIE card) -
  average of two cards".
- So **no per-card calibration of the 12 V meter exists in that source**. Every board's reading carries the same gain.
- What that source does with the reading (`runtime/PowerManager/src/power_manager_event.c`, `adcIMON12VInterruptCallback`, lines
  199-265):
  - `POWER_IN` is the instantaneous reading;
  - `AVERAGE_POWER` is a first-order, dt-weighted average with `AVERG_TIME` = 1,000,000 µs, one second (line 30);
  - the rails' readings come from the card's PMBus regulators through a running average of `N_AVE` = 100 samples at
    `MONITOR_FREQ` = 100 Hz (`IoTask.c` lines 51-52).
- **Version caveat.** Only runtime 1.7.0 is public. The cards run PMIC 1.5.0 (aifoundry2, aifoundry3), 1.3.0 (aifoundry1's card 1)
  and 1.6.1 (card 0), so the running builds' factor and averages were not read.

On the service processor (`device-bootloaders/src/ServiceProcessorBL2/services/thermal_pwr_mgmt.c` at `836a4ab60`):
- Each pass reads the PMIC's average into the SP's system-power statistic (lines 811-819) and its instantaneous reading into
  `soc_pwr_10mW` (lines 821-829).
- `DM_CMD_GET_MODULE_POWER`, which the lab's sampler reads as `board_w` (`tools/ettelem/ettelem.cpp` line 169), returns that
  instantaneous value (`get_module_soc_power`, lines 984-988; `thermal_power_monitor.c` lines 142-165). So `board_w` is refreshed
  once per SP pass.
- The governor's power arm compares the average with the TDP (`check_power_throttle_conditions`, lines 864-926).

## 2. The rails cannot place the card term

The rails come over the same PMIC, from each card's own regulators. In the public source they are no better calibrated against the
board than the board is against anything.
- **On the lab's data:** compared after each card's own V² (minion 521.6 mV on aifoundry3, 499 mV on card 1), **card 1's
  data-dependent minion-rail energy per TensorFMA step is about 1.10 times aifoundry3's**: 1.100, 1.104, 1.100 and 1.082 for pi and
  for fp32, fp16 and int8 random, at the same work per op. Before V² the two read 0.99-1.01. Source: the anatomy README, lines
  156-162 (post hoc).
- So **the lab's data cannot say whether a card term sits in the meter, the regulators or the silicon.** Card 1's 10% could be
  either rail meter's gain, or the silicon, or an on-die voltage reading about 5% off, and these data cannot separate them.
- **Treat "a rail read predicts a new card's term" only as a hypothesis.** It needs a loaded run read on both meters, so it saves
  nothing over the session anchors that term a already reads.

## 3. E64's 1.3 s on aifoundry2 is about E58's filter plus one pass

- **E64 fitted** aifoundry2's governor as "a first-order average of the board's power, time constant 1.3 s, compared with the level
  once per 0.24 s pass" (its README line 103).
- **E58 measured**, on aifoundry3, `board_avg_w` (the SP's copy of the PMIC's average) as a current 1.05 s first-order average, and
  1.10 s on card 1. It measured the rails at 1.01-1.08 s, each published one SP pass late (the pass is 0.255 s under the 10 Hz
  sampler; `05-claims.md` lines 770-773).
- **The source's average is one second** (section 1). The governor reads the SP's copy, refreshed once per pass.
- So **E64's 1.3 s is about E58's 1.05-1.10 s plus one pass of 0.24-0.26 s** (1.29-1.36 s). It is a filter close to the source's,
  seen one pass late, rather than a slower filter.
- **It is a reading, not a fit.** aifoundry2's own filter was never measured (E58's caveat), and its PMIC is 1.5.0, not the public
  1.7.0. The check is on E64's own traces, owed: set the governor model's filter from the source and E58, and fit only the latency.

09-method.md's item 1 gives the rails' running averages as 1.13 s on aifoundry2, 1.24 s on aifoundry3 and 1.15 s on card 1. Those
are the version-3 check's estimates of 26 Sep. E58's step fits of 29 Sep (1.01-1.08 s, one pass late) are the measured filter.

SPDX-License-Identifier: Apache-2.0
