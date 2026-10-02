# Finding: how this card behaves, and how to measure it without fooling yourself

[← Findings index](README.md) · no single published page; the pieces are in
[Power and temperature](https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature) (A3), [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) (A4)
and [The ET-SoC-1's DVFS loop](https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage) (A11) · numbers and sources: [05-claims.md](05-claims.md)

**Sources:** E5, E6 (telemetry and rails), E9 (the protocol), E10 (the governor), E12 (long runs), E20 and E21 (the
second card, the three machines), E27 and E29 (the rails' filter, the meter traps), R3 (the firmware policy, and since
27 September the cards' own firmware builds), E35–E46 (the three-card check's raw telemetry), E51 (the DV2 development
night of 28 September, development data, and its frozen validation on the same card, 28–29 September: TH3, TH4 and TH8
survived, TH7 fell, and TH1, TH2 and Q2 stayed untested), E54 (NV's source reading of the voltage-set command), E55–E58
(the pre-registered experiments of 28–29 September: the host link's concurrency and a host write's path, the mesh's
routing order, the memory system's rung items, the rails' filter; E55–E57 also on aifoundry2 as a third card). For
25 September: the aifoundry1 investigation and fix ([troubleshooting report](https://spacesheep.dev/@yaroslavvb/aifoundry1-troubleshooting),
[fix log](https://spacesheep.dev/@yaroslavvb/aifoundry1-fix), evidence in
[`docs/reports/data/2026-09-25-aifoundry1/`](../reports/data/2026-09-25-aifoundry1/README.md)), the read-only audit
and the fixes of the three hosts that day, and the version-3 campaign's amendments A2–A5
([`AMENDMENTS.md`](../reports/data/2026-09-25-claims-v3/AMENDMENTS.md)).

Everything here was learned by getting it wrong first. If you are about to measure power or temperature on an
ET-SoC-1, read this before designing the experiment.

**Updated 2026-09-25.** The lab now has **four cards that answer, on three firmware releases**, not two; **three are
usable for measurement**, because aifoundry1's card 0 overheats under load (amendment A4, section below). Two
statements made here before that date were wrong and are corrected below: aifoundry1's cards were refused because of
an empty driver version string, not a `srcversion` mismatch; and aifoundry3's zero TDP is set by a boot service at
every boot, not flashed. Older files (05-claims.md, 03-experiments.md E21, 16-dvfs-and-leakage.md, the DVFS page, and
the others listed in [AGENT.md](../../AGENT.md), "Known stale spots") still carry the old wording until their next
revision; this file is the current one.

**Updated 2026-09-28.** Four changes. (1) The cards do not run the governor source this file first described: the
section after the next gives the governor of each firmware build, and aifoundry2's behaviour fits its own build's
(E51, development). (2) aifoundry3's governor is latched and aifoundry1's card 1's does not raise the clock (the card
table). (3) Nothing on aifoundry2, aifoundry3 or aifoundry1's card 1 limits the die's temperature (card 0 may be an
exception): aifoundry2 ran a whole catalogue pass at a 90–103 °C mean with nothing acting (section below). (4) **aifoundry2's Master Minion hung** at 02:50:53 PDT on
28 September and took no kernel for almost six hours; the sysfs per-card reset did not recover it, and the management
reset (`DM_CMD_RESET_ETSOC`) restored it at 08:32, with the owner's approval (next section).

**Updated 2026-09-29.** (1) The mesh routes a read's reply **y first** and a write's request x first, on all three
cards (aifoundry3 and aifoundry1's card 1 at night, aifoundry2 that evening); every route on the chip diagram assumed x
first (E56; "Traps" below). (2) Two host-to-card copies in flight **on one stream** move half as much as one; one on
each of two streams lose nothing, on all three cards (E55). (3) A host write lands in its line's L3 home, and a
TensorLoad's lines stay in the L2 (E55, E57). (4) The rails' filter, measured per rail: 1.01–1.06 s on aifoundry3, but
**0.54 s on card 1's SRAM rail** (E58; the telemetry table). (5) Two firmware hazards for anyone who sets a voltage: BL2
0.18.0 writes every NoC set to flash, and a failed set retries until the watchdog resets the card (section "Setting a
rail's voltage"). (6) DV2's frozen validation on aifoundry2 ended at 16:57 PDT and was reduced (E51): no dead band
(TH3), the Master Minion's heartbeat sets the latencies (TH4) and the residency counter adds whole episodes (TH8)
survived; "an idle exit is followed at once by the idle reset" (TH7) fell, once in 52; the mean against the hottest
sensor (TH1), the 0.20.0 loop (TH2) and placement (Q2) stayed untested: the card idled at 71–76 °C for most of the
20 hours, so the heating sessions could start only in an evening cool spell and gave 4 of the 6 placement blocks and
16 of the 20 descents the rules need, and 7 of 9 separating runs fitted the mean where the rule asks for 80% (the
governor sections and the card table below). Its Master Minion ran the validation's three heating sessions without
a hang. (7) On aifoundry2 two DRAM lines that differ only in PA[17], a column bit in the L50 map, read as a row
conflict (E57; "Traps").

## aifoundry2's Master Minion hung on 28 September (02:50 PDT), and the management reset restored it (08:32)

- **What happened.** In E51's development pass p6041 the ADD run's lifts heat with `sparsity_host` (random fp32
  data, 4 minions per shire on 32 shires). A lift is not one long kernel: it is a 20,000-iteration calibration kernel
  and then a stream of short kernels for about 7 s (lift 1: 19 kernels of 0.37–0.49 s). Lift 1 ran normally (the clock
  climbed to 800 MHz, the device held 7.46 s). Lift 2 was launched 0.6 s after lift 1 ended, with the clock still at
  800 MHz; the host read the governor's idle reset to 600 MHz at 02:50:53.725, 0.13 s after the launch. Lift 2's
  calibration kernel then ran, 21 ms after that reading (02:50:53.746, 14 ms), returned ok and measured 0.77 GHz,
  between the two points. The next kernel, the first of the stream, never completed: board power fell back to the
  26 W idle and the clock stayed at 600 MHz, the host reported "kernel did not finish within 6 s, aborting the
  stream", and `timeout 10` stopped it (rc 124). The next two launches failed at runtime creation: "Couldn't use the
  HPSQ. Perhaps the Master Minion is hanged?" (rc 1). The host's kernel log has an SP runtime-error event at
  02:50:57.6 ± 0.07 s, 3.9 s after the calibration kernel ended ("ET 0000:02:00.0: Error Event Detected, Level
  Critical, SP Runtime Error, Runtime Error Count Beyond Threshold: 6"; the stamp mapped to wall time by
  `incident/kernel_events.py`, where dmesg -T prints 02:51:07). It is that counter's sixth; the first five (20, 22 and
  25 September) did not stop the card, so the event need not be the hang's.
- **What still works.** The service processor answers: at 02:52 and 02:54 it read 600 MHz, 25.9 W idle, 60 °C and a
  threshold of 65 °C. Telemetry and read-only management queries work; nothing that launches a kernel does.
- **No reset that night.** No reset was attempted (the card rules: never reset a card yourself), and no kernel ran on
  aifoundry2 until the restore.
- **Restored at 08:32 PDT, with the owner's approval; only the management reset worked.** At 06:39 the sysfs per-card
  reset (the lab admin's) re-attached the device (the kernel log's
  "enabling device" and "added peer-to-peer DMA memory"), but the Master Minion stayed hung: launches at 06:40 and
  06:47 failed at runtime creation with the same "Couldn't use the HPSQ" message. At 08:32:45 the management reset
  (`dev_mngt_service -m DM_CMD_RESET_ETSOC -n 0`, the reset used twice on 18 September) recovered it: the driver logged
  "Device is resetting" for about 6 s and re-attached the device at 08:32:52, and at 08:33 a test on 1 minion ran
  3 launches of 0.49 s, each ok, at 600 MHz (the device held 1.65 s). **Lesson (one case): the sysfs reset did not recover a
  hung Master Minion; the management reset did.** Either is a card reset: the lab admin's or the owner's call, never
  an agent's. The SP's uptime and throttle residencies after the reset are not in the record. The DV2 validation
  (frozen) started on the restored card at 20:45:39 PDT the same day; its three heating sessions (22:13–23:56) ran 52
  launches, every one returning 0, 7 of them launched 0.49–0.58 s after the previous one ended as lift 2 was, and the
  Master Minion did not hang (E51); the validation ended at 16:57 PDT on 29 September.
- **Cause: not established.** The night's 43 launches before it, which all ran (probes, smokes, runs, and lifts
  launched 0.52–0.58 s after the previous one ended, four times), with 57 climbs and 26 full descents of the clock, did not hang
  (`raw/p*/launches.jsonl`). That this launch met the 800 → 600 MHz idle reset is a hypothesis, not a finding.
- **Evidence:** `docs/reports/data/2026-09-28-dvfs2-aifoundry2/raw/ALERT-MM-HANG.json` and `raw/p6041/`
  (`launches.jsonl`, `heater-1-pre.out.gz`, `tel-1.jsonl.gz`), the later read-only watch cycles `raw/p1111/z1.json`
  and `raw/p1112/z1.json`, `incident/` (the kernel log's error events, `kernel_events.py`; the restore,
  `recovery.txt`: the commands, the launches' output and the kernel-log lines) and `dv2.json` `incident`.

---

## The clock governor is thermal first

The [service processor](README.md#terms) runs a power-management task (`thermal_pwr_mgmt.c`, R3), once per
management pass: 133 ms on aifoundry2, 135 ms on aifoundry1's card 1 and 224 ms on aifoundry3 with nothing polling,
longer while a sampler polls (E41; the table below). It steps the minion operating point **down** when the die's
reading is above a software threshold (**65 °C**) or the board's power is above the TDP level (**65 W**), and **up**
when a kernel runs and neither is. The thermal branch is checked first and wins. The reading it compares is one
number in every firmware build: the integer mean of the **34 minion-shire sensors**, each truncated to a whole degree
(the I/O shire's sensor is not in it), tested as `mean > 65`. No build has a per-sensor or hottest-sensor path to the
clock. E51's development runs agree: in 12 of 12 runs the clock held 800 MHz for at least a second after the hottest
sensor read 67 °C or more, and on an idle card whose mean read 64 °C while the hottest sensor read 66 °C the governor
stayed out of its thermal state. Its frozen validation (28–29 September, the same card) saw the same, in 17 runs over 6
blocks (G1-H PASS), and no step near the hottest sensor's first 66 °C; but its test of the step's timing needed 80% of
the runs that separate the two rules to fit the mean and got 7 of 9, and its idle test got 4 of the 5 cycles it needs,
so by its rules the question is untested and the source is the answer. How the governor responds beyond that depends on the
build, and the cards do not run the `353f20e` source this file first described: see "The clock governor, by firmware
build" below. [16-dvfs-and-leakage.md](16-dvfs-and-leakage.md) has the `353f20e` loop in detail.

This card's operating points, read from telemetry (E10):

| Point | Clock | Die voltage |
|---|---|---|
| lowest | 600 MHz | 516–518 mV |
| middle | 700 MHz | 568 mV |
| highest | 800 MHz | 618–620 mV |

**Consequence:** a card that has been busy usually idles above 65 °C (72–80 °C on 20–22 September; about 65 °C on
23 September, when the governor did intervene) and therefore runs *everything* at 600 MHz, whatever the power — which is why an earlier version of this work
concluded, wrongly, that "the clock never moves". It moves only from a cool die. aifoundry2's rest is not steady: on
the night of 28 September its idle reading swung between 59 and 72 °C on a 10–30 minute scale (72, 70, 64, 67, 69,
64 °C at 00:40–01:30 PDT, 59–62 °C from 02:30), with idle power following at about 0.4 W per °C (25.7 W at 59 °C,
31.1 W at 72 °C). The host's ACPI zones read a constant 16.8 and 27.8 °C (probably not live readings), its drive
43–47 °C and its CPU package 37–59 °C. What drives the swing is not established (E51, development).

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

**Firmware 1.4.1 idles at 300 MHz** (aifoundry1's card 0, 2026-09-25). Between kernels this release puts the minions
in a `low_power` state at 300 MHz and 398 mV (18.6–18.8 W board power). In a clock test (two 2 s random fp32 matmul
launches 1 s apart, 10 Hz telemetry) the first launch after such an idle showed no power rise and reached 600 MHz
(501–519 mV) only at its end; the second drew 49.4 W, and the card then idled at 600 MHz (26 W). So on this card:

- an idle bracket is at a different operating point from the 600 MHz burst it brackets, and a rule that drops a
  burst when *any* sample is off 600 MHz drops every burst unless it looks only at samples taken inside the kernel
  (amendment A2 in [`AMENDMENTS.md`](../reports/data/2026-09-25-claims-v3/AMENDMENTS.md));
- the first launch after a low-power idle can run slow or late: make a warm-up launch first.

Firmware 1.2.0 (aifoundry1's card 1) and 1.3.1 (aifoundry2 and aifoundry3) idle at 600 MHz. At 600 MHz the three
releases idle very differently: 26 W (1.4.1), 33–35 W (1.2.0 at 57–62 °C) and 32 W (1.3.1, aifoundry2 at 74 °C).

## The clock governor, by firmware build

The pages first described the governor at et-platform `353f20e` (R3). The cards run older builds, read on
27 September in the same clone (`external/et-platform`, `device-bootloaders/src/ServiceProcessorBL2/services/thermal_pwr_mgmt.c`
at each commit). The table is read from source; the entries marked *seen* have card evidence.

| | `353f20e` (= `836a4ab`) | BL2 0.20.0: release 1.3.1, aifoundry2 and aifoundry3 (closest public source `ffca4cbb4` = `cafe03fc3^`, 17 May 2024) | BL2 0.18.0: release 1.2.0, aifoundry1's card 1 (closest `da192816a`, 27 March 2024) |
|---|---|---|---|
| When the thermal test acts | only while a kernel runs | **always, busy or idle** (*seen*: 18 of the 20 thermal entries of E51's night came after the SP's own idle line; in its validation 51 idle entries, I5 PASS) | as 0.20.0 |
| Thermal response | one table point down per pass | **a blocking loop**: one point down, sleep 1,000 ticks (about 0.40 s), read the mean again, repeat while it is above 65; meanwhile the power branch, the idle reset included, cannot act (*seen*: 17 of 17 idle episodes under 60 s lasted k × 0.4053 s to within 1.4 ms, k = 0–3, E51; in its validation 44 of 46 within 10.9 ms, and the two longest, 20 and 21 periods, 17–21 ms short, so TH2 is untested; E10's down-steps paired 0.4–0.5 s apart) | as 0.20.0 |
| Leaving the thermal state | — | at a mean of 65 or less, to the boot point (600 MHz); on the next pass a busy card under the TDP **climbs to the top point in one call** (*seen*: 57 of 57 climbs showed at most one 700 MHz sample, E51; 67 of 67 in its validation, G2-C PASS) | as 0.20.0 |
| Power test | the PMIC's average | the PMIC's **instantaneous** reading; the loops exit on the average, the power-down loop at under 1.05 × TDP or at 300 MHz | as 0.20.0 |
| Operating points | the flash VMIN table (600, 700, 800 MHz on aifoundry2) | the same table | **fixed 50 MHz steps between 300 and 700 MHz**, the voltage computed from the boot point |
| Hysteresis | none | none: in above 65, out at 65 (*seen*: all 20 entry lines of E51 printed 66, all 20 exit lines 65; in its validation 51 entries at 66, 52 exits at 65 or less, 92 up-steps from 65 or less: TH3 survived) | none |
| The PMIC alarm (75 °C, 75 W) | a 300 MHz safe state | a safe state that never ends and sets the frequency register but not the PLL (source only) | a real 300 MHz safe state |

aifoundry1's card 0 runs release 1.4.1 (BL2 0.21.2), whose governor acts only while a kernel runs (the card table).
What each card shows:

- **aifoundry2 behaves as 0.20.0 predicts.** Its SP's throttle residency (a read-only management query, E51) put it in
  the thermal state for 747,342 s, 8.65 of its 9.23 days of uptime, with one stay of 2.1 days: whenever its rest is above
  65 °C it sits in the thermal loop at 600 MHz, and its idle reset waits. Every idle exit (20 of 20) was followed by the
  SP's own idle line, 17 of them one pass later (0.119–0.131 s) (E51, development). In the frozen validation (28–29
  September) 51 of 52 idle exits were, and one was followed 5 ms later by a new entry into the loop, so "an exit is
  followed at once by the idle reset" (TH7) fell; the THERMAL_DOWN counter added whole episodes (6 intervals within
  0.2 ms: TH8 survived), and the launch and end latencies fit the Master Minion's heartbeat (launch to 800 MHz a median
  0.67 s, at most 1.2 s; kernel end to 600 MHz at most 1.09 s: TH4 survived).
- **aifoundry3's governor is latched.** Under 0.20.0 its boot-time TDP of 0 W sends the first kernel after boot into a
  power-down loop that can never exit (the exit needs an average under 1.05 × 0 W, or 300 MHz, and the clock is already
  at the bottom point), so the power task spins; the first time the mean then passes 65 °C the thermal state is set and
  nothing clears it, and no governor line is ever logged again. That fits the record: 26 throttle-down and 27 idle lines
  in one window on 22 September, none in any version-3 dump (E41, TEL-G), and E51's one read-only query of its residencies
  on 28 September: power-up, power-down, thermal-down and power-safe all 0 after 2 days 8 hours of uptime, although the
  heat-placement runs of 27 September had taken its die past 66 °C (development, one reading). Its clock cannot move at
  any temperature, and a reset by the lab admin would return it to live DVFS until its boot service runs again.
- **aifoundry1's card 1 does not raise its clock.** In the three-card check it read 600 MHz in all 318,667 samples,
  and the SP's own minimum and maximum of the clock read 600/600 in every one (a statistics reset does not clear them,
  so they reach back before the check), although 9,461 of them were busy at 45–65 W at a die of 64 °C or less (its 65
  blocks started at 56–69 °C, median 62 °C) and its mean reached 88 °C. E48's gathers-and-scatters passes, filed in the
  same tree, are not counted (with them: 359,687 and 11,612). A live 0.18.0
  governor would have stepped to 650 MHz or 550 MHz there. Active power management switched off, or a latched state,
  would each explain it; they are not told apart (the power-up residency since boot would narrow it).

## Nothing limits the die's temperature (aifoundry2, aifoundry3, aifoundry1's card 1)

The one hardware trip in the firmware is a PMIC alarm at 75 °C or 75 W (`TEMP_THRESHOLD_HW_CATASTROPHIC`,
`POWER_THRESHOLD_HW_CATASTROPHIC`), written into the PMIC as its own alarm thresholds. It takes its temperature from
the PMIC, not from the die's sensors. The SP reads the PMIC's system temperature only when it starts or resets its
statistics (`thermal_pwr_mgmt.c:2995–3001` at `ffca4cbb4`, under the note "PMIC is currently reporting system
temperature as 0") and feeds that statistic's minimum and maximum a literal 0 on every other pass (`:663–664`), so
`sp.system_c` is not a per-sample reading of the PMIC: it read 0 on all three cards throughout the check, which says
only that the PMIC gave 0 at each reset. The evidence that nothing acts is the telemetry below. The host field
`temp_c.pmic` is the minion-shire mean again, not a PMIC reading. So at the bottom operating point nothing on aifoundry2, aifoundry3 or aifoundry1's card 1 acts on the
die's temperature:

- **aifoundry2 ran a whole catalogue pass at a 90–103 °C mean.** The version-3 catalogue's hot pass 11
  (`docs/reports/data/2026-09-25-claims-v3/raw/aifoundry2/cat/p11/`, 26 September, 02:26–02:31 PDT) heats the die to at
  least 88 °C before each configuration and has no upper stop, and its launches ran from 91 to 102 °C with no heater
  (`run.log`). Its mean read above 90 °C in 2,565 of 2,567 samples and peaked at 103 °C, with the hottest sensor at
  106 °C, the I/O shire at 101–102 °C and the board at up to 86.9 W (83.6 W at the first 103 °C reading), all at
  600 MHz, with no safe state. That is above the 90 °C at which this work's long runs stop (the owner's rule), and
  nothing tripped. In all, aifoundry2's mean passed 90 °C in eight version-3 telemetry files (12,176 samples: catalogue
  passes 6, 9 and 11, full-catalogue passes 22 and 31, the matmul benchmark's thermal passes 3 and 4, and X5's pass 3),
  every one at 600 MHz.
- **The one possible exception is aifoundry1's card 0** (release 1.4.1, not in the campaign): it read 115–117 °C after
  its smoke blocks of 25 September before it dropped to 300 MHz (the section on that card below); whether its PMIC's
  safe state or 1.4.1's idle point did that is not established.

The only guard is the runners' own cap: stop at a mean of 90 °C (`tools/ettelem/run_horace_long.sh`, the DV2 watcher).
A runner that holds a temperature needs an upper stop too; the version-3 catalogue runner
(`tools/claims-v3/cat/run_catalogue_t10.py`) has none. The counts here: `python3 tools/claims-v3/dv2/recount_v3.py
over90` (every telemetry file whose mean passed 90 °C), `… pass` (catalogue pass 11), `… systemc` (`sp.system_c`) and
`… cool-busy` (aifoundry1's card 1, above), each over the three-card check's passes only (E48's `gs/` passes, filed in the
same tree, come in with `--with-gs`), so they equal the DVFS page's counts (`dvfs.json` `v3.sp_readouts`).

## Setting a rail's voltage: two firmware hazards (read from source for E54, 28 September)

NV (E54) sets the mesh (NoC) rail with `DM_CMD_SET_MODULE_VOLTAGE`. Reading that command's path in each build the cards
run found two hazards; neither has been triggered on a card, since no voltage has been written yet.

- **BL2 0.18.0 writes every NoC voltage set to flash** (release 1.2.0: aifoundry1's card 1). Its
  `pwr_svc_set_module_voltage` calls `flash_fs_set_vmin_lut_boot_voltages()` for the NoC, which erases and
  reprograms the 4 KB asset-config sector (the part number and the VMIN table) that the boot code takes the NoC rail's
  boot voltage from. The write came in with et-platform `5f5c37abf` (2024-03-20) and went out with `dd8927ce5`
  (2024-04-05); 0.20.0 (`ffca4cbb4`, aifoundry2 and aifoundry3) does not write the flash. On card 1 every set would
  become the boot voltage, a crash before the restore would leave it booting at the new value, a reset during the
  erase could corrupt the sector, and the flash write's status replaces the set's own. NV refuses any BL2 below 0.19.0
  and does not use card 1.
- **A failed set retries until the watchdog resets the card.** On 0.20.0 the command's range check
  (`pmic_set_voltage`: 400–600 mV) returns its error into `Thermal_Pwr_Mgmt_Set_Validate_Voltage`'s retry loop, which
  counts its retries down only on the on-die (PVT) failure branch. A range error, or a regulator write or read-back
  that fails, loops inside a critical section until the service processor's 10 s watchdog resets the SoC. 0.18.0 has
  no range check at all. The fix, et-platform `7c6049087` (2024-10-10), is later than the lab's builds, so a whitelist
  of values in the caller is the only guard (NV sends only 485, 540 and 600 mV). A reset also clears aifoundry3's
  clock guard until it runs again.

The source reading is in `tools/claims-v3/nv/DESIGN.md` §2 and §9. Setting a voltage changes a shared card's state:
it is the owner's call (the lab rules below).

## The telemetry, and what each number really is

`tools/ettelem` reads the management library directly (`libDM.so`), which exposes more than the stock CLI:

| Field | Meaning | Gotcha |
|---|---|---|
| `board_w` | board power, 10 mW steps | refreshed once per service-processor pass, and a poller lengthens the pass: under ettelem at 10 Hz a new value every 156 ms on aifoundry2, 158 on aifoundry1's card 1 and 263 on aifoundry3; with nothing polling the pass is 133, 135 and 224 ms (E41, 26 September); near-instantaneous otherwise |
| `sp.minion_w`, `sram_w`, `noc_w` | per-rail power | **the PMIC's running average, first-order, published one SP pass late** (E58, pre-registered): τ minion 1.06 s, SRAM 1.01, NoC 1.04 on aifoundry3; minion 1.08 and NoC 1.08 on aifoundry1's card 1, but **its SRAM rail 0.54 s**, so the cards' SRAM meters differ. (E27's single-parameter τ ≈ 1.15–1.22 s folded the SP's pass into τ; a step reaches 55–57% after 1 s and 83–84% after 2 s as read.) The published rail split (the last 0.6 s of a burst, divided by 0.94) assumes τ near 1.1 s: on the catalogue's 3.2 s bursts it errs by −1.8 to −4.3% on every rail but card 1's SRAM rail, where it errs by +5.5% (offline, `tools/claims-v3/tau/PREREG.md`). `tools/ettelem/deconv.py` undoes the filter with each card's τ (a burst's energy within 0.3% of the step on aifoundry3). The SP copies the reading each pass (so on aifoundry3 the copy changes only every 263 ms under ettelem); not a moving average. Skip 2–3 s after any change before averaging. `ettelem sample --reset-ms` resets the statistics on a schedule, and the reset also restarts the running average: with a reset every second, one second after a burst the rail has fallen 93% of the way on every card (E41) |
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
  the cause is on the card. E41 (26 September) placed it in the SP's loop: with nothing polling, a pass takes 224 ms
  on aifoundry3 against 133 ms on aifoundry2 and 135 ms on aifoundry1's card 1; why aifoundry3's loop is slower,
  with the same firmware release as aifoundry2, is not established.
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

## The lab machines and their four cards are not interchangeable

Updated 2026-09-25: aifoundry1's two cards answer since 15:02 that day, so there are four cards on three firmware
releases; three are usable for measurement, since aifoundry1's card 0 overheats and takes nothing sustained (amendment
A4). Before using a card for anything comparative, read its governor configuration. Two read-only commands:

```
gcc -O2 -I/opt/et/include -o etcfg tools/etcfg/etcfg.c && ./etcfg   # the driver's view: TDP, boot clock, shire mask, cache sizes
LD_LIBRARY_PATH=/opt/et/lib build/ettelem/ettelem config           # the firmware's view: TDP, threshold, power state
```

On aifoundry1, prefix `ET_DEVICES=<n>` to address card n (below). `ettelem config` opens the management node, so
check first that nobody holds the card (`et-who`).

**The live dashboard reads every card's temperature once a second (since 2 October 2026, the owner's decision).**
`tools/lab/live/live-collector.py` runs `ettelem temp` (two management requests, about 4 ms including process start)
on each card whose link is up, and only while `et-who --check` finds no holder of any card node or lock on that
machine, so it never locks a user out. The management node admits one opener (the driver returns EBUSY to a second
one, `et-soc1-pcie.c` `esperanto_pcie_mgmt_open`), and the runtime's default device layer opens only the ops node,
so ordinary card programs never collide with it. A tool that opens the management node (ettelem, `dev_mngt_service`,
et-powertop, the dashboard's 30-minute sample, a reset) and starts in one of those 4 ms windows gets EBUSY: retry it.
Take the card lock before starting such a tool and the collector stays off the card for as long as you hold it.

| | aifoundry2 | aifoundry3 | aifoundry1 card 0 | aifoundry1 card 1 |
|---|---|---|---|---|
| Firmware release (BL / PMIC / minion) | 1.3.1 (0.20.0 / 1.5.0 / 0.23.0) | 1.3.1 (the same) | 1.4.1 (0.21.2 / 1.6.1 / 0.24.0) | 1.2.0 (0.18.0 / 1.3.0 / 0.22.0) |
| TDP the driver reports | 65 W | 65 W | 65 W | 65 W |
| **TDP the firmware uses** | **65 W** | **0 W**, set at every boot (below) | 65 W | 65 W |
| Clock | firmware DVFS: 600, 700 or 800 MHz; above 600 only below about 68 °C. In this chassis the die never read below 65 °C in the version-3 campaign (336,070 samples, 25–26 Sep), and over DV2's 20 h validation (28–29 Sep) it idled at 71–76 °C in 327 of 378 cycles, so it runs at 600 MHz unless it starts cold | **600 MHz** (NoC 400), never seen higher (10 Hz telemetry); its governor is latched by the zero TDP: no governor line in its trace since 25 Sep (E41 TEL-G), and its throttle residencies all 0 after 2 d 8 h up (28 Sep; E51, development); it makes no thermal step at any temperature | firmware DVFS; **idles at 300 MHz** (`low_power`); its 0.21.x governor acts only while a kernel runs (firmware source, 27 Sep) | **600 MHz in all 318,667 samples of the three-card check (25–26 Sep)**, and in the SP's own minimum and maximum, although 9,461 were busy at 45–65 W at 64 °C or less and the mean reached 88 °C: its governor does not raise the clock (active power management off, or latched; asked the lab). Its build steps 50 MHz between 300 and 700 MHz, so it could never reach 800 |
| Idle | 31–36 W at 73–80 °C (27 W cold); on the night of 28–29 Sep (DV2's idle watch) 73–75 °C and 31.4–32.5 W at 20:45–21:09 and 00:11–01:00 PDT, 59 °C and 25.4–25.6 W at 22:12 and 23:15–23:18 (idle cycles only; its heating sessions ran 22:13–23:56); over the whole watch, to 16:48 on 29 Sep, 59–76 °C, 71–76 °C in 327 of 378 cycles, and never below 65 °C after 23:18 | 23.6 W at 50 °C (25.1 W at 56 °C under the runs); the die idles at 55–57 °C since the host changes of 25 Sep | 18.6–18.8 W at 300 MHz; 26 W at 600 MHz | 33–35 W at 600 MHz and 57–62 °C |
| Use it for | the main card | compare switching power over idle, never absolute watts | **nothing sustained: it overheats** (below) | anything; it peaked near 71 °C under the campaign's smoke blocks |
| Version-3 campaign | yes | yes | excluded (amendment A4) | yes |

The hosts differ too. Host-side timing (launch, synchronisation, copies, compile times) is not comparable between
them; card-side numbers (cycles, power at a fixed operating point) do not depend on the host.

| | aifoundry1 | aifoundry2 | aifoundry3 |
|---|---|---|---|
| CPU, RAM, BIOS | i7-11700K (8 cores, 16 threads), 128 GB (4 × 32 GB DDR4-3200, two channels), F5 | i5-11600 (6 cores, 12 threads), 64 GB (2 × 32 GB DDR4-2666, two channels), F5 | i7-11700K, 32 GB (**one** DDR4-2666 DIMM: a single memory channel, so host memcpy runs at 9.2 GB/s against 17.4 and 21.4; E50), F6 |
| `/opt/et` runtime and device layer | a local build of an et-platform fork (May 2026): its `libetrt.so` and `libdeviceLayer.a` differ from the others; the device layer honours `ET_DEVICES=<n>` and takes the DRAM ranges from the driver. Older ET copies in `/usr/local/bin` (February 2026: `esperanto_flash_tool`, `profiler_converter`) come first on PATH | the stock et-platform `353f20e` build (December 2025), runtime 0.19.0 | `353f20e`, except `libetrt.so`: a patched Release `-O3` build of `836a4ab` (2026-07-23, an event-id guard) |
| The same on all three | the `et_soc1` driver 0.20.0 (one source since aifoundry1's fix), `libDM.so`, `dev_mngt_service`, `et-powertop`, and the RISC-V GCC 15.1, which generates identical code on all three (see Traps) | | |

**aifoundry3 is pinned at 600 MHz by a zero TDP.** The governor's step-down test is `measured power > TDP` and its
step-up test is `<`. At a TDP of zero the first is always true and the second never is, so the loop logs a
throttle-down at every kernel start, and nothing can ever step it up. The card's own log says so: `Power throttle
down event, current pwr 35380  tdp level: 0`, 26 times in one 8 KB window, alternating with idle events, with no
step-up event at all. A second reading agrees: `get_power_state()` classifies a card as `MAX_POWER` exactly when
power exceeds the TDP, and aifoundry3 reports `max_power` while drawing 23 W. Since 25 September it logs nothing at
all: under its own 0.20.0 build the zero TDP leaves the power task in a loop that cannot exit, and the first mean
above 65 °C then latches the thermal state for good ("The clock governor, by firmware build", above).

**Correction (2026-09-25): the zero is not flashed.** Until then this file said the TDP was flashed. A boot
service on aifoundry3, `et-board-clock-guard.service` (in place since 2026-07-23, noting that the card is unreliable
above 600 MHz), sets the static TDP level to 0 and the clocks to 600 MHz (minion) and 400 MHz (NoC) at every boot
through the management commands `DM_CMD_SET_MODULE_STATIC_TDP_LEVEL` and `DM_CMD_SET_FREQUENCY`. A card reset returns
the card to its firmware's own DVFS until the guard runs again. The open question of E21, "why is it zero", is
answered: it is the lab's deliberate setting.

**The driver will not warn you.** Its `ETSOC1_IOCTL_GET_DEVICE_CONFIGURATION` reports the nameplate 65 W on
all four cards, including aifoundry3's. Any host-side check passes. The card works; it is simply held at
600 MHz, the bottom of its VMIN table (the firmware's table of operating points), for as long as its TDP stays at
zero.

**aifoundry1: why its cards were refused until 25 September.** The `et_soc1` module that DKMS built there had an
**empty version string**: `/sys/module/et_soc1/version` held only a newline, where the other hosts have `0.20.0`. The
device layer's driver check reads that file right after `open()`, finds no `x.y.z` and throws `Error unable to
evaluate compatibility!`, so every tool on `libDM.so` or the device layer failed before a command reached the card.
The cause was a one-character Makefile typo in the stale DKMS source snapshot (et-platform `09531e5c1`, fixed
upstream five days later in `78ed9b0d6`). **Correction:** this file used to blame a `srcversion` mismatch with
`libDM.so`. No code reads `srcversion`; it differed only because of the typo and an `#if` that compiles to the same
code. `tools/etcfg` worked throughout, because it issues the raw ioctl without the device layer. Rebuilding the module
from the fixed driver source, an admin task, fixed it on 25 September at the repo owner's request (the fix log above).
After any driver change, the discriminating check is `cat /sys/module/et_soc1/version` = `0.20.0`: `ls -l /dev/et*`
(mode 0666) and `lspci -k` prove nothing.

**aifoundry1's card 0 overheats.** On 25 September about ten minutes of short smoke blocks took its die to 98–102 °C.
Right after them it read 115–117 °C with nothing running and drew 66–71 W at 600 MHz (leakage at that temperature),
until its firmware dropped it to 300 MHz and it cooled from 104 to 78 °C in eight minutes. Card 1 beside it peaked
at about 71 °C under the same smokes. It is a cooling fault (fan, heat sink or airflow) that the 300 MHz low-power idle
hides. Do not run sustained work on it. The machine's login banner says so, and the campaign excludes it (A4). The
same card's PCIe link also logs about one corrected receive error per second at its root port, at a rate that
changes from boot to boot. It does not stop the card, but link replays can add DMA latency. A reseat is pending. Since
25 September the kernel log for that link is rate-limited, and the error counters still count.

**Selecting one card on a two-card host.** With aifoundry1's device layer, `ET_DEVICES=<n>` makes a program open only
card n, which it then sees as device 0; programs built on aifoundry1 against its `/opt/et` honour it, `ettelem`
included. `tools/claims-v3/lib.sh` sets it from `V3_DEVICE=<n>`. `/opt/et/bin/dev_mngt_service` (and
`et-powertop`) is the stock build: it ignores `ET_DEVICES` and opens every card's management node even with
`-n <N>`, so run it only when both cards are free (`et-who`). On 26 September our stock `dev_mngt_service` call for card 1 collided with a
watcher holding card 0: 13 refused opens in the kernel log and 10 aborts with core dumps.

**Leave the cards' configuration alone.** aifoundry3's clock guard is deliberate. Changing a TDP, a clock, the
firmware or the driver on a shared machine silently changes what other people's runs measure, in the middle of their
experiments. Those are lab-admin decisions: ask. The same goes for resets. A lab admin can reset one card through
the sysfs per-card reset (the lab admin's): on 25 September that brought aifoundry3's card back
in about 8 s with no host reboot, after which its clock guard had to run again. Reloading the kernel module does not
reset a card's firmware. Do not reset a card yourself ([getting-started.md](../getting-started.md) §2, lab norms).

## Host changes of 25 September, and what stays comparable

Between 16:14 and 16:27 PDT on 25 September the three hosts were brought to one configuration (the machine fixes the
owner asked for). What each change means for measurements:

| Change | Card side (cycles, power at a fixed operating point) | Host side (launch, sync, copies, `took_ms`) | Earlier data still comparable? |
|---|---|---|---|
| Host CPU power profile `performance` (was `balanced`) | unchanged, but the hosts run warmer: aifoundry3's idle die went from 53–54 °C to 55–57 °C (amendment A5) | faster, less jitter | card side yes, at a matched die temperature; host side **no** |
| chrony replaces systemd-timesyncd | no | no | yes; timestamps now agree across hosts better than the earlier ±20 ms |
| systemd-coredump keeps cores | no | a crashing launch takes longer to exit while its core is written | yes |
| Full package upgrade, installed; the reboot into kernel 7.0.0-34 is still pending | at the reboot the cards are re-initialised (same firmware and driver code) | at the reboot: a new kernel (IOMMU, DMA and interrupt paths) | card side yes; host side: take a new baseline after the reboot |
| `et-who`, card lock files, login banner, `et-lab-manifest`, a persistent journal, clean-ups | no | no | yes |

Record the output of `et-lab-manifest` with every run (host, kernel, CPU and power profile, clock sync, driver
version, PCIe link per card, library hashes and aifoundry3's clock-guard marker), and the card's firmware from your
own tool: the manifest does not open the card, so it cannot read the firmware.

## Comparing cards: use switching power, not watts

aifoundry3 idles 11 W below aifoundry2 and at a different temperature, so absolute board power tells you
nothing across cards. What compares cleanly is **switching power**: board power during a run minus the idle
power measured just before it, which cancels that card's leakage at that temperature. On that basis the two
cards agree to 8%, and one scale factor removes even that. See [11-thermal-model.md](11-thermal-model.md).

## Retraining a card's PCIe link hung aifoundry1 (30 September, 14:41 PDT)

**Never retrain, re-speed or reset a card's PCIe link on a running host.** On 30 September, to learn whether the
corrected-error flood on aifoundry1 card 0's link (about one a second at 16 GT/s since the 18 September boot) came
from a marginal signal or from a lane or the slot, the owner ran, as root and with card 0 idle and locked, our
"Gen3 test" (lab report U25): set the target speed of card 0's root port (`0000:00:01.0`) to 8 GT/s with `setpci`
(Link Control 2) and retrain the link (Link Control, bit 5). Two readings at 16 GT/s a minute apart went through
(76 corrected receiver errors at the root port, none at the card). At the retrain, 14:41:21, **the whole host**
stopped: no more output, no Tailscale, no ARP on the LAN. It stayed down until Roman power-cycled the lab at about
15:07 (all three machines were cycled together). Our plan had said a failed retrain would drop only card 0.

What we know, read as our user after the boot:

- No panic record: `systemd-pstore` found the persistent store empty at boot, so this looks like a hard hang,
  not a kernel panic (`kernel.panic` is 0 on these hosts, so a panic would not reboot either). The previous
  boot's kernel log needs root or the adm group: `journalctl -b -1 -k -o short-precise | tail -80` as root on
  aifoundry1 is the next thing to read.
- The root port has AER and DPC (downstream port containment) under OS control. Candidate causes, none tested:
  the link failed to train at 8 GT/s and went down, DPC or AER recovery removed the card under the `et_soc1`
  driver, and the driver or the CPU hung on the vanished device (a completion timeout on an MMIO access can
  freeze an Intel host); or the 11th-generation CPU root port does not tolerate a speed change forced by
  `setpci` on a Gen4 link.
- After the cold power cycle card 0's link trained at 16 GT/s x8 and its root port counted **no** corrected
  errors in the first minutes, where it had counted about one a second for twelve days: the flood may have been
  a bad training at the 18 September boot, not the slot. Watch the count (`et-lab-health`, or
  `grep RxErr /sys/bus/pci/devices/0000:00:01.0/aer_dev_correctable`) before concluding.

Lessons: a link-level experiment is a host-level risk, so it needs someone on site and nobody else working on the
host; the lab has no console or out-of-band access, so a hung host costs everyone until someone walks over; and a
power cycle clears `/tmp` on every machine it hits (aifoundry2's 19 GB of working files since 28 September were
lost; keep work in the home directory). The incident page:
https://spacesheep.dev/@yaroslavvb/aifoundry1-link-retrain-hang

## aifoundry2's card dropped off the bus while idle (1 October, 09:42 PDT)

At 09:42 on 1 October aifoundry2's card stopped answering on PCIe while nothing used it: both ends of the link
logged corrected receiver errors, then the link went down for good (configuration space read all ones, the root
port saw no receiver). It stayed down until a full-reset power cycle at 06:45 on 2 October
(`echo pci > /sys/kernel/reboot/type`, mode cold, then a reboot: the chipset drops the supply's main rails, which
power-cycles the slot); a plain warm reboot keeps the slot powered. Confirmed again on 2 October: a plain
`systemctl reboot` at 10:47 left the card off the bus (no device at all under root port 00:1b.0), and the full reset at
10:53 brought it back at 16 GT/s x8. **To recover a card that fell off the bus, always the full reset, as root:**
`echo cold > /sys/kernel/reboot/mode; echo pci > /sys/kernel/reboot/type; systemctl reboot` (the setting lasts one boot).
After that boot the idle card heated from 45 to 55 °C in its first two minutes (the live collector's records). **The card's temperature follows the host's CPU
load, not its own work**: 63–67 °C while the host was busy, 70 °C idle in the evening, 82–83 °C idle from 02:30 on
1 October (idle power up from 29 to 37.5 W), and it failed minutes after the host went idle again; aifoundry3's card,
on the same Gigabyte Z590 AORUS MASTER board in the same slot, stayed at 54–57 °C. The chassis fans most likely
follow the CPU temperature (no fan speeds are visible from Linux). Fix on site: the BIOS fan settings (Smart Fan 5:
Fan Stop off, a floor of at least 50%), copied from aifoundry3 (lab report SH5). Until then, a host that sits idle
lets this card overheat, and no firmware cut-off stops it.

## Traps that cost time here

- **A card's queue counters race with its resets (30 September, from the driver source).** The world-readable sysfs files `mgmt_vq_stats/*` and `ops_vq_stats/*` (`msg_count` and its siblings) walk the driver's queue tables with no lock, and et-driver 0.20.0 (the same as upstream's latest, 836a4ab) shows them before it builds the tables and removes them after it frees them. A read during a card reset can return garbage (a jump of trillions of messages); one during a driver load can crash the reader. Tools that read them (our usage logger, the dashboard) discard impossible jumps; never poll them in a tight loop, and never read `utilization_percent`. Reported on the Requests for Roman page (C29, CF13); the upstream issue is drafted ([02-requests.md](02-requests.md), Q86).
- **`sparsity_host --budget` defaults to 8 seconds** on silicon and silently stops a longer run. Raise it for
  anything past 8 s.
- **`pgrep -f` over `ssh` matches itself.** The processes that run a remote command carry the whole command in
  their own command lines (Tailscale SSH's `tailscaled be-child ssh … --cmd=<the command>`, and the `bash -c` that
  runs a compound command), so `ssh host '… pgrep -f run_queue.sh …'` always finds a process: its own. On
  27 September that made a starter on aifoundry3 refuse twice. Bracket the first letter
  (`pgrep -af '[r]un_queue.sh'`), and never `pkill -f` over `ssh`. For "is the card free?" keep only `et-who`'s lines that start with `/dev/et` or `lock:` (or use
  `et-who --check`, exit 0 free, 1 held, 2 failed, where the 27 September version in `tools/lab/` is installed):
  the idle sentence was read as a holder the same evening.
- **Never edit a runner script while it is running.** Bash reads the file as it executes; a mid-run edit
  aborted a four-hour session at the last step. An `scp` over a running script corrupts it the same way, and an
  `scp` to a new path drops the executable bit. Replace a script with `mv` (or `os.replace`) onto the old name, and
  `chmod +x` after copying (2026-09-24).
- **`hpmcounter3` reads 128 short** when its low 7 bits are 0–10 (E2). Correct it (`fixcyc()`); the firmware's
  four-reads workaround does not fix it.
- **Kernel code that traps or faults** (collected 2026-09-25 from the pages that found each):
  - no 64-bit integer-to-float conversion: `fcvt.s.lu` traps (cause 0x1e), and so does a `double` anywhere in a
    kernel, a checksum accumulator included. Use 32-bit counters in floating-point loops, and sum bit patterns as
    integers;
  - in U-mode, `fdiv`, `fsqrt`, `frsq`, `fsin`, the integer divides and remainders of the packed unit, and reading
    the `cycle` CSR trap ([energy manual 3a](../energy-manual/03a-every-instruction.md) lists the thirteen);
  - offset 0 of a shire's scratchpad faults: start buffers 256 KB in;
  - a global atomic through the scratchpad self ID `0x7F` is a bus error
    ([18-on-chip-relay.md](18-on-chip-relay.md), "Things that bit us");
  - never spin on a global atomic in a barrier: past 24 requesters the line's home shire loses its own memory path
    and the barrier hangs. Use the credit-release barrier `workloads/nocbench` measures
    ([17-hot-line.md](17-hot-line.md)).
- **`evict_va` is asynchronous.** Fence and wait a few hundred cycles before timing, and note the level codes
  name where the line is *left* (1 = L2, 2 = L3, 3 = memory).
- **The L1 data cache is not coherent** and writes back whole 64 B lines. Harts on different minions must not
  share a line.
- **Only hart 0 of a minion may issue tensor ops**, except `TensorLoadL2Scp`/`TensorWait`.
- **Never let a minion receive readies from two `TensorSend` partners at once** — one ready bit per minion, not
  per partner. By the RTL rule a lost ready leaves that receiver, and its sender, waiting until the chip is reset.
  Seen once on silicon (aifoundry2, 18 September, two pairs through one minion with no barrier between them; not
  repeated): the stalled harts ignored the firmware's abort, and every later launch failed with
  `KernelLaunchCmIfaceMulticastFailed` until the chip was reset. `sys_emu` tracks partners separately and does not
  catch it.
- **The environment is not stationary.** Mid-session the lab's airflow changed and the die fell 12 °C under an
  unchanged workload. Record enough telemetry to notice. Other users are part of the environment too
  (2026-09-25): CI runners on aifoundry1 and aifoundry2 can take a card at any time, and a demo service on aifoundry3
  can launch on its card without taking the card lock. Check `et-who` before and after a run. The hosts reach the
  network over Wi-Fi only and roam between access points: aifoundry2 lost its Tailscale connection for 12 minutes on
  23 September. Start long runs detached (`setsid`, [getting-started.md](../getting-started.md) §7).
- **aifoundry3 can be heated.** Earlier sessions never took it past about 61–66 °C, but those were short bursts:
  150 back-to-back 2 s random fp32 matmul launches took its die from 55 to 88 °C (V3-IDLE, pass 1, 2026-09-25).
  Its heat sink is faster than aifoundry2's, not unbounded.
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
- **aifoundry3's host programs crash about 1.08 s after they start** (2026-09-25). About one launch in 100 dies
  with SIGSEGV (rc 139, or −11 from Python), always 1,078–1,080 ms after it began, during device setup and before
  any result: seen in `sparsity_host`, `enercat_host`, `nocbench_host` and `onchip_host`, never on aifoundry2 in the
  same runs. **Cause** (four core dumps): libetrt's thread-pool workers log at the custom g3log levels
  `VERBOSE_HIGH/MID/LOW` (`ThreadPool::workerFunc`, `common-sw/src/threadPool/src/ThreadPool.cpp:81`), which only
  `logging::LoggerDefault` registers (`common-sw/src/logging/include/hostUtils/logging/Logger.h:57-59`). A host
  program that never constructs it leaves them unregistered, so the first `LOG(VLOG_MID)` from several new workers
  inserts the level into g3log's `std::map` of levels from all of them at once, while `IRuntime::create` is still
  starting threads, and the map is corrupted. aifoundry3's `-O3` `libetrt.so` hits the window; aifoundry2's build
  has not been seen to. `tools/g3log-race/` reproduces the race without a card (6–7 % of trials corrupt the map;
  none once the level is registered first). **Fix:** every `workloads/*/host/main.cpp` now calls
  `registerRuntimeLogLevels()` first in `main`; a new host program must do the same (or construct
  `logging::LoggerDefault`). On the card it holds: aifoundry3 ran the fixed gather/scatter build for 641 host
  processes on 26 September without a crash (6.4 expected at the old rate). Binaries built before that change, the
  version-3 campaign's among them, can still crash: treat such a launch as failed and repeat it. Cores are kept: `coredumpctl list`, `coredumpctl gdb <pid>`.
- **`ettelem sample` sometimes fails to start** right after a previous instance was stopped (about one start in
  three). The runners retry until the telemetry file has a line (`start_sampler` in `tools/claims-v3/lib.sh` and
  the `tools/ettelem/run_*_power.sh` scripts).
- **Health checks that mislead.** `DM_CMD_GET_FIRMWARE_BOOT_STATUS` fails with status −16006 even on a working
  card, so it is no test. `dev_mngt_service -m DM_CMD_GET_MODULE_FIRMWARE_REVISIONS -n 0 -u 5000` is the good first
  query (it also prints the firmware release). After a driver change, check `/sys/module/et_soc1/version`
  (`0.20.0`), not the device nodes' mode or `lspci`. "Cannot be opened" can mean that the library refused after
  `open()`, while `tools/etcfg` still works (aifoundry1 until 25 September).
- **The three hosts' toolchains generate identical code** (checked 2026-09-25). The same sources give kernel ELFs
  with different md5s on the three hosts, but only the `.comment` section (the compiler's version string)
  differs. Compare and record the `.text` hash, not the file's. One real difference: an LTO object compiled on
  aifoundry2 or aifoundry3 is zstd-compressed and aifoundry1's `lto1` cannot read it, so build on the host that
  links. **Correction:** a note of the same morning said the toolchains differ and produce different code; they do
  not.
- **Two host-to-card copies in flight on one stream move half as much as one** (E55, aifoundry3, aifoundry2 and
  aifoundry1's card 1, pre-registered). At 2 × 64 MB, DMA-only, they moved 0.488 of one at a time on aifoundry3 and
  0.496 on aifoundry2 (the rate itself 0.484 and 0.491 over 1–64 MB), while one copy on each of two streams moved 1.012
  and 1.014: nothing lost. Splitting a copy into elements changes nothing. To overlap host-to-card copies, give each its
  own stream. Card to host does not collapse (1.10 at 2 × 64 MB on both).
- **Read data cross the mesh y first; write data x first** (E56, all three cards, pre-registered). With flows chosen to
  share one link under only one order, reads' replies collided only under y first and writes' requests only under
  x first, so a reply retraces its request's path. Until 29 September every route drawn on the chip diagram and on heat per
  mm, and E32's link-sharing counts, assumed x first for all traffic; both pages now draw read data y first, and under
  y first E32's all-pairs set shares 0 / 22 / 30 / 55 / 78% of its link-hops at 1 / 2 / 3 / 4 / 6 hops, against
  0 / 22 / 32 / 55 / 72% under x first (`wire.json` `checks.link_sharing.<cfg>.shared_link_hop_fraction_yx`).
  Recompute a route's links before reasoning about contention. A
  directed link saturated near 92 GB/s.
- **A host copy leaves its lines in the L3, and a TensorLoad leaves them in the L2** (E55, E57; aifoundry3 and aifoundry2,
  as card 1 in development). After a staged host copy, 99.5–99.6% of a buffer's lines read at L3 latency, whether the L3
  held them before or not (a host write goes through the line's L3 home, which allocates it); a second TensorLoad of the
  same 1 KB took 199 cycles, an L2 hit, against 744–748 from the L3 and 1,342–1,345 for the first. A probe that means to
  time DRAM or the L3 must evict first and time only fresh lines; a stream that reuses its buffer measures the L2 after
  its first pass.
- **aifoundry2's DRAM may not split rows and columns as the other cards do** (E57, 29 September, pre-registered). Two
  lines of one row that differ only in PA[17], a column bit in the L50 map, read as a row conflict on aifoundry2 (0
  cycles from the other-row reference, 48 trials), where aifoundry3 and card 1 read them as the same row (−21 cycles);
  the other 14 conditions, and the bank bits, behaved as the map says. On 19 September the anatomy's one-bit flip of
  PA[17] on the same card read as the same row (−12 cycles), by a different method, so why is not established. A probe
  that relies on row hits within PA[13–17] should check that card first.
- **aifoundry1's card 1's SRAM rail averages over 0.54 s, not about 1 s** (E58). Deconvolve each card's rails with its
  own τ (`tools/ettelem/deconv.py` has them), and do not compare card 1's SRAM rail split with another card's.

## Related

- [16-dvfs-and-leakage.md](16-dvfs-and-leakage.md): the governor in detail, and the second card's zero TDP (written
  before the 25 September corrections above).
- [What is broken on aifoundry1](https://spacesheep.dev/@yaroslavvb/aifoundry1-troubleshooting) and
  [aifoundry1 is fixed](https://spacesheep.dev/@yaroslavvb/aifoundry1-fix): the empty driver version, found and
  fixed on 25 September.
- [`../lab-access.md`](../lab-access.md): the machines' shared tools (`et-who`, the card locks, `et-lab-manifest`) and
  access; [`../../AGENT.md`](../../AGENT.md): the entry point for working in this repository.
- [19-observability-and-the-unmetered.md](19-observability-and-the-unmetered.md): what the meters miss, and the
  improvement ladder.
- [11-thermal-model.md](11-thermal-model.md): the thermal network and the step-time trick for the whole-degree
  sensor.
- [03-experiments.md](03-experiments.md): the standard protocol and every session's command; E51 is the DV2
  development night of 28 September (the governor's build, the mean against the hottest sensor, the Master Minion hang)
  and its frozen validation's verdicts; E54 is NV (not yet run); E55–E58 are the pre-registered experiments of
  28–29 September behind this file's 29 September changes.
