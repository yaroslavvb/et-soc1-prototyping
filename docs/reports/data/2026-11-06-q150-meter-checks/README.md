# Q150(inv-lab), post hoc: card 1's SRAM-rail reading mixes two quantities; the die's voltage monitors agree with the regulators' set points; no rail reaches its 16-bit field

*Fri 6 Nov 2026 (week 45), about 14:40 PST, on the Intel, desk only. No card, lab box or device was touched, and nothing was
sent to a card. Q150 is the owner's question of that afternoon: whether the card's power can be read more accurately, whether
the card has more sensors than the lab uses (per shire, in particular), and whether a sensor might be wrong. These checks were
made while taking the lab's inventory of every power, current, voltage and temperature reading the cards give (the inventory
lane, inv-lab). **Every figure here is POST HOC**: read from committed telemetry that existed before the checks were thought of.
None is a verdict, and no committed number, rule or verdict changes.*

## Results first

1. **Card 1's SRAM rail (aifoundry1 card 1, PMIC firmware 1.3.0) is fed at least two different quantities within each PMIC
   scan. No other rail on any card is.** The version-3 check's TEL block reset the statistics every second
   (`ettelem sample --reset-ms 1000`, 25-26 Sep 2026, three passes a card: 147 reset windows on card 1, 126 on aifoundry2 and
   126 on aifoundry3). Within those windows, on steady samples (700 ms or more after the reset, the board within 0.5 W of the
   previous sample and of the PMIC's board average for the SRAM rows, within 0.3 W for the minion and NoC rows), medians:

   | card, rail | samples | PMIC min / average | PMIC max / average | average, W |
   |---|---:|---:|---:|---:|
   | card 1, SRAM, idle | 219 | **0.627** | **1.592** | 2.482 |
   | card 1, SRAM, board at 40 W or more | 61 | **0.631** | **1.575** | 2.663 |
   | card 1, minion | 209 | 0.980 | 1.022 | 13.313 |
   | card 1, NoC | 209 | 0.962 | 1.036 | 4.891 |
   | aifoundry2, SRAM, idle | 215 | 0.976 | 1.022 | 2.003 |
   | aifoundry3, SRAM, idle | 254 | 0.978 | 1.022 | 2.125 |
   | aifoundry2 and aifoundry3, minion and NoC | 192-226 | 0.952-0.974 | 1.025-1.049 | |

   (SRAM rows: `reset_minmax_bylevel.json`; minion and NoC rows: `reset_minmax_steady.json`, whose card-1 SRAM row, 0.627 and
   1.591 over 209 samples, agrees; `reset_minmax.json` takes every sample 600 ms or more after a reset, loads included, and
   gives card 1's SRAM rail 0.638 and 1.606.) After each reset, every rail's PMIC average restarts within 2% of its
   window's last reading by its first non-zero sample (0.980-1.003), on every card, except card 1's SRAM rail, which restarts
   at **0.77** of it and climbs over about 0.7 s (0.770, 0.821, 0.872, 0.916, 0.937, 0.970, 0.975 at 100 ms steps from 300 ms;
   `reset_recovery.json`, idle windows).
   - **It fits the public PMIC firmware's two-phase SRAM path.** In `aifoundry-org/et-boards` at `e5e0cf2` (runtime 1.7.0),
     `firmware/et-soc1-pmic/runtime/PowerManager/src/IoTask.c` scans two SRAM phases on the default hardware (`scanListTbl`,
     lines 918-935; another board encoding scans one SRAM module instead, lines 940-946 and 320-330), and lines 1041-1048
     update the SRAM statistic twice per scan: first with phase 0's reading alone, then
     with phase 0 plus phase 1 (current and power summed). The running average is `N_AVE` 100 updates (lines 51-52, 884), so
     two updates per 10 ms scan settle in about 0.5 s instead of 1 s. That is E58's measured 0.54 s on this rail
     (`../2026-09-29-tau-aifoundry1-c1/`; `docs/findings/05-claims.md` line 772), against 1.01-1.08 s on every other rail
     measured. Card 1 runs PMIC 1.3.0, whose source is not public, and aifoundry2's and aifoundry3's SRAM rails (PMIC 1.5.0)
     show neither signature, so the mechanism is a hypothesis: a firmware version, a board revision, or both.
   - **What it implies.** Card 1's SRAM average is a mix of readings, not the rail's power. If the summed reading is the
     rail's power, the rail carries about **1.6 times** what the average reports. The energy manual's off-rail fit gives card
     1's SRAM rail a coefficient of **0.540** (± 0.020, HC3), against 0.034 and 0.043 on aifoundry2 and aifoundry3
     (`docs/energy-manual/04a-fine-grain.md` line 200): with those cards' coefficient as the rail's own delivery loss, that
     is about **1.5 times** the reading. The two estimates agree to about 7%. Neither is a measurement.
   - **What it touches** (none re-derived here): card 1's rail splits, its SRAM-rail rows in the energy manual's leakage
     table (`04a-fine-grain.md` lines 113-154), its off-rail line and fit, the anatomy's card-1 SRAM lines
     (`../2026-11-05-q145a-anatomy-top-lines/README.md`), and the 0.54 s deconvolution constant, which describes the mix,
     not the rail.
   - **What would settle it:** the PMIC 1.3.0 source; or a card-1 run that steps the SRAM rail's load in reset windows and
     reads its minimum and maximum (phase readings would scale with the load); or the phases' own readings, which the
     service processor does not forward.

2. **The die's voltage monitors agree with the regulators' set points on the three metered rails, within 2 mV, on every
   card.** Same windows, idle samples (board under 40 W): the on-die average (`die_mv`, `DM_CMD_GET_ASIC_VOLTAGE`) less the
   PMIC's set point (`reg_mv`, `DM_CMD_GET_MODULE_VOLTAGE`), medians:

   | card | minion | SRAM | NoC | DDR | Maxion |
   |---|---|---|---|---|---|
   | card 1 | 499 against 500 (−1 mV) | 751 / 750 (+1) | 486 / 485 (+1) | 762 / 800 (−38) | 591 / 600 (−9) |
   | aifoundry2 | 518 / 520 (−2) | 704 / 705 (−1) | 484 / 485 (−1) | 767 / 800 (−33) | 586 / 600 (−14) |
   | aifoundry3 | 523 / 525 (−2) | 698 / 700 (−2) | 484 / 485 (−1) | 767 / 800 (−33) | 591 / 600 (−9) |

   (`setpoint_vs_die.json`, 1,091-1,316 samples a card.) The −1 to −2 mV is about the firmware's own double truncation
   (et-platform `836a4ab`, `driver/pvt_controller.c`: each shire's reading to a whole millivolt in `pvt_vm_conversion`, then
   the integer mean in `GET_MINION_VM`). The DDR and Maxion rails read 33-38 and 9-14 mV under their set points; whether that
   is a drop or a monitor offset is not separated here. So on these rails the cards' voltages differ by set point, not by a
   monitor offset: card 1's minion rail runs at 500 mV and aifoundry3's at 525 mV, and the monitors read them to 1-2 mV. A
   V² comparison between the cards (the anatomy's card-1 excess of about 10% after V²) is therefore not explained by an
   on-die voltage reading a few percent off, on September's set points. It does not test the regulators' own accuracy, and
   October's set points (E78's and E82's 521.7 and 498.7 mV) were not re-read here.

3. **No committed rail reading reaches the 16-bit milliwatt field.** The service processor masks each PMBus statistic to 16
   bits (`PMB_STATS_MASK 0xffff`, et-platform `836a4ab`, `driver/pmic_controller.c` line 91), so a rail's watts top out at
   65.535 W. Over E80's 24,427 committed samples on aifoundry2 (fp32 random at 800 MHz among them), the highest minion-rail
   average is **42.12 W** and the PMIC's running maximum **55.19 W**; the board read 88.09 W at most (`rail_max_e80.txt`).

## Builds on

- **Checked:** the prior-work inventory, read Fri 6 Nov 2026 about 14:25 PST. Public rows read: P03, L11, H28. The ids are
  opaque pointers into a private inventory.
- **Used:** the version-3 check's TEL block and its raw files (`../2026-09-25-claims-v3/raw/<card>/tel/p<n>/reset.jsonl.gz`;
  `tools/claims-v3/tel/README.md`); E58 (`../2026-09-29-tau-aifoundry1-c1/`, `../2026-09-29-tau-aifoundry3/`); the energy
  manual's off-rail fit (`docs/energy-manual/04a-fine-grain.md`, `../2026-09-23-energy-manual/unmetered_fit.json`); E80's
  telemetry (`../2026-10-31-e80-kinds-speed/`); the public PMIC firmware (`aifoundry-org/et-boards` `e5e0cf2`) and service
  processor firmware (`aifoundry-org/et-platform` `836a4ab`), the sources `09-method.md.dated-note-1.md` reads.
- **Not used:** card 0, which has no committed reset-window telemetry; the card schematic's sense network.
- **Tiers:** public only.

## Files

| file | what |
|---|---|
| `reset_minmax.py`, `reset_minmax.json` | each rail's PMIC min/average and max/average, every sample 600 ms or more after a reset |
| `reset_minmax_steady.py`, `reset_minmax_steady.json` | the same on steady samples (0.3 W bound), with the rails' watts |
| `reset_minmax_bylevel.py`, `reset_minmax_bylevel.json` | the SRAM rail on steady samples (0.5 W bound), idle and board at 40 W or more |
| `reset_recovery.py`, `reset_recovery.json` | each rail's average after a reset, relative to its window's last sample, by 100 ms of time since the reset |
| `setpoint_vs_die.py`, `setpoint_vs_die.json` | on-die voltages against the PMIC's set points, idle samples |
| `rail_max_e80.py`, `rail_max_e80.txt` | E80's highest rail and board readings on aifoundry2 |
| `SHA256SUMS` | the files above |

From the top of the repository:

```
RAW=docs/reports/data/2026-09-25-claims-v3/raw; D=docs/reports/data/2026-11-06-q150-meter-checks
python3 -I $D/reset_minmax.py $RAW > $D/reset_minmax.json
python3 -I $D/reset_minmax_steady.py $RAW > $D/reset_minmax_steady.json
python3 -I $D/reset_minmax_bylevel.py $RAW > $D/reset_minmax_bylevel.json
python3 -I $D/reset_recovery.py $RAW > $D/reset_recovery.json
python3 -I $D/setpoint_vs_die.py $RAW > $D/setpoint_vs_die.json
python3 -I $D/rail_max_e80.py docs/reports/data/2026-10-31-e80-kinds-speed > $D/rail_max_e80.txt
```

SPDX-License-Identifier: Apache-2.0
