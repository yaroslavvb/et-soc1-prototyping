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

**Updated 2026-10-23.** E64 read the governor's own log through every run on aifoundry2: on a die below 65 °C only
the power test acts (a dither around a ~1 s average of the card's power, not its instantaneous reading), at a reading
of 66 °C only the thermal test acts, and the trace ring carries binary records the old reader stopped at ("Which limit
acts, read from the governor's own log", below).

**Updated 2026-10-09.** **aifoundry2's card is back in service** since that afternoon: the stalling 120 mm fan clipped
under the card was replaced by a two-fan 92 mm PCI-slot bracket in the slot beside it, and the card now idles at 51 °C
and 23.2 W, levels off at 62–63 °C under the 8-minute sgemm burst test and settles at 75 °C and 59 W under 10 minutes
of full load, with no stop ("aifoundry2's card back in service: a two-fan bracket at the card", below). So all four
cards are in service. Long full-load runs still keep a temperature stop: the margin is 1.2 times today's cooling.

**Updated 2026-10-07.** **aifoundry2's card is out of service again** since 16:46 PDT that day: idle, a day after the
6 October fan fix, the cooling at the card got worse (at 03:55, and again at about 14:25) and the card ran away to a
138 °C mean and dropped off the PCIe bus, as on 2 October ("aifoundry2's card ran away again at idle", below). So three
cards are in service: aifoundry3's and aifoundry1's two.

**Updated 2026-10-02.** (1) **aifoundry1's card 0 is back in service**: its fan was found broken and replaced on
site, and the owner put the card back in service at about 13:30 PDT. It idles at 49 °C, and 8 minutes of sgemm bursts
held it at a 52–53 °C mean (hottest sensor 56 °C), cooler than card 1 under the same test (59–60 °C); select it with
`ET_DEVICES=0` and `etsoc-shire0.lock` (its section below keeps the September record). (2) **aifoundry2's card is out
of service**: idle, with nothing on it, it heats until it drops off the PCIe bus (a 138 °C mean and 134 W at 12:02 PDT,
69 minutes after a full-reset boot), and no firmware cut-off acts ("aifoundry2's card dropped off the bus while idle",
below). So three cards are in service: aifoundry3's and aifoundry1's two. (3) The live dashboard reads every free
card's temperature once a second (the section on the lab machines).

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

🛑 **Dated: these are the releases as recorded in September, and card 0 no longer idles at 300 MHz.** All four cards
report release 1.4.0 / BL1–BL2 0.22.0 since 27–31 October 2026 (the card table). On 31 October aifoundry1's card 0 read
1.4.0 / BL2 0.22.0 / PMIC 1.6.1 / minions 0.25.1 (E84 A1) and idled at **600 MHz / 519 mV, 19.0–21.2 W**, between all 35
of E84's runs; its telemetry of 20 October idled at 600 MHz too (6,047 of 6,133 idle readings, E60). Its only 300 MHz
readings on 31 October were the PMIC alarm's safe state ("aifoundry1 card 0's PMIC over-power alarm", below). The 25
September observation above stands for its date.

## Power is an offset plus a per-hart term (aifoundry2, 21 October 2026, E62)

E62-CAL put the card on a ladder (the `hp` heater kernel over 128, 256, 384, 512 and 1,024 harts, each an 8.5 s
launch, the statistic the **median of the 10 Hz board samples in the last 4.0 s**), and the card is linear in harts but
**not through zero**: switched board W = **5.80 ± 0.30 W + 55.8 ± 1.0 mW per hart** (the six clean rungs, 128–512
harts). Idle before it: 22.69 W at 600 MHz, die 49 °C.

| harts | board W | switched W | die °C |
|---|---|---|---|
| 128 (B4C, 4 × 32) | 35.45 | +12.75 | 52 |
| 128 (W8B_16, 8 × 16) | 35.69 | +13.00 | 53 |
| 128 (INT16_8, 16 × 8) | 35.95 | +13.26 | 53 |
| 256 (CEN8) | 42.71 | +20.02 | 56 |
| 384 (W12) | 49.39 | +26.70 | 58 |
| 512 (INT16) | 57.40 | +34.71 | 61 |
| 1,024 (UNI32) | 66.45 | +43.76 | 63, throttled |

- **Do not price work per hart from zero.** 128 harts read 2.5× a linear-from-zero model and 512 harts 1.7×; the fixed
  ~5.8 W (clock tree, leakage, the rails coming up to 617–621 mV under any load) is 45% of the smaller reading.
- **The offset cancels in a constant-hart swap, and only there.** Moving the same number of harts across the die
  changes the board reading by ~0.3 W; any pattern-against-idle statistic carries the whole offset.
- **Geometry costs almost nothing:** three 128-hart legs at per-shire 32, 16 and 8 agree within 0.51 W, rising with
  the die's warm-up across the ladder rather than with geometry.
- **The governor takes 1,024 harts over:** the UNI32 rung ran an 800 → 700 → 600 → 700 MHz limit cycle through its
  whole 8.6 s, board 52 / 66 / 86 W. 768 harts at per-shire 24 is already governor territory (E62-BLOOM: die 69 °C,
  45% of on-phase samples below 800 MHz). **192 harts (12 shires × 16 or 8 × 24) is the quiet operating point:** every
  12-shire swap held 62.5–63.5 °C and 800 MHz at about 43 W board.
- **Read power with a median.** The board meter drops 5–12 W for a sample or two at random, and the DVFS ramp at each
  launch's start (the card idles at 600 MHz between launches) puts sub-800 MHz samples into every launch's first ~1.2 s:
  separate ramp samples from governor samples by their offset into the launch.

## The clock governor, by firmware build

The pages first described the governor at et-platform `353f20e` (R3). The cards run older builds, read on
27 September in the same clone (`external/et-platform`, `device-bootloaders/src/ServiceProcessorBL2/services/thermal_pwr_mgmt.c`
at each commit). The table is read from source; the entries marked *seen* have card evidence.

| | `353f20e` (= `836a4ab`), BL2 0.22.0: the version all four cards report since 27–31 Oct 2026 (E69, E79, E82 A1, E84 A1; no card exposes a BL2 git hash) | BL2 0.20.0: release 1.3.1 — 🛑 **no card reports it now: aifoundry2 read release 1.4.0 / BL1–BL2 0.22.0 under E69 on 27 Oct 2026, and aifoundry3 the same under E79 on 31 Oct** (“The governor's two knobs”, below) (closest public source `ffca4cbb4` = `cafe03fc3^`, 17 May 2024) | BL2 0.18.0: release 1.2.0, aifoundry1's card 1 as recorded until 31 Oct 2026, when it read 1.4.0 / BL2 0.22.0 (E82 A1) (closest `da192816a`, 27 March 2024) |
|---|---|---|---|
| When the thermal test acts | only while a kernel runs | **always, busy or idle** (*seen*: 18 of the 20 thermal entries of E51's night came after the SP's own idle line; in its validation 51 idle entries, I5 PASS) | as 0.20.0 |
| Thermal response | one table point down per pass | **a blocking loop**: one point down, sleep 1,000 ticks (about 0.40 s), read the mean again, repeat while it is above 65; meanwhile the power branch, the idle reset included, cannot act (*seen*: 17 of 17 idle episodes under 60 s lasted k × 0.4053 s to within 1.4 ms, k = 0–3, E51; in its validation 44 of 46 within 10.9 ms, and the two longest, 20 and 21 periods, 17–21 ms short, so TH2 is untested; E10's down-steps paired 0.4–0.5 s apart) | as 0.20.0 |
| Leaving the thermal state | — | at a mean of 65 or less, to the boot point (600 MHz); on the next pass a busy card under the TDP **climbs to the top point in one call** (*seen*: 57 of 57 climbs showed at most one 700 MHz sample, E51; 67 of 67 in its validation, G2-C PASS) | as 0.20.0 |
| Power test | the PMIC's average | the PMIC's **instantaneous** reading; the loops exit on the average, the power-down loop at under 1.05 × TDP or at 300 MHz (**E64, *seen* on aifoundry2: the input the card logs at each power step behaves as a ~1 s running average**, 65.0–67.9 W while the board read 80–83 W, and each step is one point per pass; "Which limit acts", below) | as 0.20.0 |
| Operating points | the flash VMIN table (600, 700, 800 MHz on aifoundry2) | the same table | **fixed 50 MHz steps between 300 and 700 MHz**, the voltage computed from the boot point |
| Hysteresis | none | none: in above 65, out at 65 (*seen*: all 20 entry lines of E51 printed 66, all 20 exit lines 65; in its validation 51 entries at 66, 52 exits at 65 or less, 92 up-steps from 65 or less: TH3 survived) | none |
| The PMIC alarm (75 °C, 75 W) | a 300 MHz safe state (*seen* on aifoundry1's card 0, 31 Oct 2026: the 75 W over-power alarm on fp32 random data, E84; below) | a safe state that never ends and sets the frequency register but not the PLL (source only) | a real 300 MHz safe state |

aifoundry1's card 0 was recorded as release 1.4.1 (BL2 0.21.2) until 31 Oct 2026, when it read 1.4.0 / BL2 0.22.0
(E84 A1), the `353f20e` column's version: its governor acts only while a kernel runs, and its PMIC's over-power alarm
is a third limit ("aifoundry1 card 0's PMIC over-power alarm", below).
What each card shows:

- **aifoundry2 behaves as 0.20.0 predicts.** Its SP's throttle residency (a read-only management query, E51) put it in
  the thermal state for 747,342 s, 8.65 of its 9.23 days of uptime, with one stay of 2.1 days: whenever its rest is above
  65 °C it sits in the thermal loop at 600 MHz, and its idle reset waits. Every idle exit (20 of 20) was followed by the
  SP's own idle line, 17 of them one pass later (0.119–0.131 s) (E51, development). In the frozen validation (28–29
  September) 51 of 52 idle exits were, and one was followed 5 ms later by a new entry into the loop, so "an exit is
  followed at once by the idle reset" (TH7) fell; the THERMAL_DOWN counter added whole episodes (6 intervals within
  0.2 ms: TH8 survived), and the launch and end latencies fit the Master Minion's heartbeat (launch to 800 MHz a median
  0.67 s, at most 1.2 s; kernel end to 600 MHz at most 1.09 s: TH4 survived).
- **aifoundry3's governor is latched.** (🛑 **The mechanism below is 0.20.0's and is build-specific:** at BL2 0.22.0 there is no such loop at all — the throttle check is a single pass per DM-task pass and the 1.05 guardband macros are never used — so on that build a TDP of 0 is a *reversible pin* at the VMIN floor, as E72 measured on aifoundry2. aifoundry3's own build was not queried in Q129; E79 read it on 31 Oct 2026 — release 1.4.0, BL1 and BL2 0.22.0 — so this mechanism no longer describes it, and its TDP of 0 is a reversible pin; see “The governor's two knobs”, below.) Under 0.20.0 its boot-time TDP of 0 W sends the first kernel after boot into a
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
  would each explain it; they are not told apart (the power-up residency since boot would narrow it). Under the BL2
  0.22.0 it reports since 31 Oct 2026 (E82 A1) it still reads 600 MHz in every sample, busy or idle (E82, E88, E91),
  so the 0.18.0 reading above does not explain it either.

## Which limit acts, read from the governor's own log (aifoundry2, 23 October 2026, E64)

E64 (pre-registered, `tools/claims-v3/hpl/`) ran the Horace matmul from a cool die across ten fp32 operand patterns and
three minion counts, from a heated die, and for 75 s at a time, and dumped the service processor's trace ring after
every run. The ring names the cause of every step, so no step had to be inferred:

- **Below 65 °C only the power test acts, and it acts alone.** 98 power throttle-downs, every one in the
  cool-die blocks, at a die reading of 57–63 °C; the governor's logged power at each was 65.0–67.9 W.
  Every run whose work drew 67 W or more at 800 MHz got one first; no run under 62 W got any (rules R1, R2). The line is
  the watts, not the data: random normal data on 768 minions (69 W) was stepped down, on 640 (62.5 W) it was not.
- **At a reading of 66 °C only the thermal test acts**, at any power: 104 thermal throttle-downs, 102 logged at
  66 °C and 2 at 67 °C (the first readings over the line), including ones and zeros at 34–55 W, under the power
  level, with no power step beside them (R3).
- **The power loop is a dither on an average.** At a cool die, random fp32 on the full card goes 800 → 700 → 600 → 700
  → 800 MHz, one point per pass (~0.24 s under a 10 Hz sampler), drawing ~82 / 64 / 50 W at the three points, while
  the governor's logged input at its steps stays between about 58 and 68 W. A model, a first-order average of the board's power with a 1.3 s time
  constant compared with 65 W once per pass (step down if over, up if under, no dead band), reproduces the mean clock
  of every cool-die run to 3.3 MHz rms (`surface_hpl.py`). So **the power test reads a ~1 s running
  average, not the instantaneous value**: the table above says "instantaneous" from the `ffca4cbb4` source, and the
  card's own log disagrees (its power throttle-down lines read 65.0–67.9 W while the board read 80–83 W). A burst
  shorter than about a second at 800 MHz never meets the power level.
- **A power throttle-down is not sticky.** The clock climbs back within a pass or two (the source reading of P5, that
  the power-down state lasts until the idle reset, was wrong).
- **Sustained:** in 80 s runs (nine 8 s processes back to back) the die passes 65 °C for anything that draws more than about 50 W: the line through the nine runs' last 40 s reads 65.5 °C at 50.3 W of board power (0.47 °C per W). So on the bracket's cooling **the thermal test, not the power test, sets a sustained matmul's clock**: random fp32 and fp16 data first read 66 °C 8–9 s in and end pinned at 600 MHz with the die at 66–67 °C (the table has no lower point to take), fp32 and fp16 ones settle near 738 MHz and int8 random near 763 MHz, all under the thermal test, while zeros hold 800 MHz at 59 °C (R4). Sustained, zeros run 33% faster than random fp32 data (12.3 against 9.2 TFLOPS), against 13% from a cool die.
- **The trace ring holds more than text.** Next to the CRITICAL lines the 1.3.1 build writes a `New OP: Freq <MHz>
  MNN <mV> (V) SRM <mV> (V)` line at every operating point set and a 16-byte binary power-status record (power W,
  throttle state, power state, temperature °C, target MHz). `tools/claims-v3/dv2/sptrace_events.py` stops at the first
  binary record and loses everything after it (7–29 of 60–71 entries in E64's smoke); read the ring with
  `tools/claims-v3/hpl/sptrace_full.py`. Placing entries on the host clock works best by matching the `New OP` lines to
  the sampler's clock changes (one offset per run; the SP's tick is 1 µs).
- **The sampler's board value trails the clock by about two samples** (0.2 s at 10 Hz): the board reading is
  refreshed once per SP pass and read a pass late, so a power paired with the clock in the same sample is the previous
  operating point's. Shift it before reading power per clock (`surface_hpl.py` picks the shift per run).
- **A random-data heater cannot take this die past about 67 °C** on the bracket's cooling: the power test holds it near
  65 W, and above 65 °C the thermal test holds it at 600 MHz, where random data draws about 50 W (E64 amendment A2).

## The governor's two knobs, moved for the first time (aifoundry2, 27 October 2026, E69 and E72)

Everything above about the cap was read from the governor's own log, with the cap never moved. On 27 October 2026 the
owner authorized one card's governor to be moved (Q129), and E69 and E72 moved it under the ET-SoC-1 firmware field
manual's G0–G4 gates, each with a change record committed beside its data
([`tools/claims-v3/knob/CHANGE-RECORD.md`](../../tools/claims-v3/knob/CHANGE-RECORD.md),
[`tools/claims-v3/lq6/CHANGE-RECORD.md`](../../tools/claims-v3/lq6/CHANGE-RECORD.md); PASS / FAIL / UNKNOWN per gate,
UNKNOWN never read as PASS). Only two fields were ever written — `DM_CMD_SET_MODULE_STATIC_TDP_LEVEL` and
`DM_CMD_SET_MODULE_TEMPERATURE_THRESHOLDS` — in **41 DM set/restore commands** (E69's 39 across five sessions, E72's
2), every one `rc 0`, with **zero read-back mismatches**, inside the code-enforced bounds (TDP 30–65 W, threshold
60–70 °C). **No OTA, flash, PMIC command, card reset, PCIe recovery, driver reload or clock set at any point.** The
measurements are in [03-experiments.md](03-experiments.md), E69 and E72; what belongs here is what the cards and the
firmware turned out to be.

**Firmware read fresh, and the card table above was stale.** Under E69's G0 gate (13:56–13:58 PDT) aifoundry2's card
reports **release 1.4.0, BL1 and BL2 0.22.0, PMIC 1.5.0, minions 0.25.1** — not the 1.3.1 / BL2 0.20.0 / minion
0.23.0 this file carried — and the `0.20.0` in `et-lab-manifest` is the **host driver's** version, not the card's.
aifoundry3's card was **not** re-read in Q129 (E79 read it on 31 Oct 2026: **release 1.4.0, BL1 and BL2 0.22.0, PMIC
1.5.0, minions 0.25.1**), so the "aifoundry2 and aifoundry3" mapping that the 0.20.0 column of
"The clock governor, by firmware build" used to carry no longer maps a card to a build: **read each card's own
versions before citing a source behaviour.** E64's measurements stand; the source citations under them point at the
wrong build. (The `353f20e` column is itself fine — it is the 0.22.0 snapshot, and it already says "one table point
down per pass" and "the PMIC's average", which is what the card does.)

**Both set paths write one service-processor RAM word and never flash (BL2 0.22.0; field-manual rule 8).** The two
commands land in `g_soc_power_reg` and `g_pmic_power_reg`, `volatile` structures in the service processor's plain
`.data` RAM (`services/thermal_pwr_mgmt.c:143-144`) — not a memory-mapped window, not flash — so a governor setting
is **lost at an SP reset**. Every flash writer in the whole BL2 0.22.0 tree lives in `driver/flashfs.c`
(`flash_fs_write_partition`, `flash_fs_erase_partition`, `flash_fs_set_part_number`, `flash_fs_set_vmin_lut`,
`flash_fs_write_config_region`, `flash_fs_increment_*_boot_count`) and **none of them is reachable from either set
path**. That is what makes a governor move legal under rule 8, and it is **build-specific**: at BL2 0.18.0 (release
1.2.0, aifoundry1's card 1 as recorded until 31 Oct 2026, when it read BL2 0.22.0, E82 A1) a NoC **voltage** set did
write the flash ("Setting a rail's voltage", above, and
[05-claims.md](05-claims.md) § NV). 🛑 Two residuals E69 records rather than hides: the card exposes **no BL2 git
hash** through any allowed query, so the source read establishes the behaviour of *a* 0.22.0; and the `et-platform`
copy read was a **single shallow commit** of an in-development 0.22.0 whose `[Unreleased]` changelog carries both
SW-21990 and SW-22147 — so "both plausible builds agree" holds for the two **set** paths and emphatically **not** for
the governor's power branch.

**A TDP of 0 pins this card at 600 MHz, and writing the TDP back releases it.** E72 wrote one field twice. 125 of 125
kept runs and 215 of 215 smoke samples sat at exactly **600 MHz, 517.9 mV**; after the restore the card stepped
**600 → 700 → 800 MHz inside one 6 s launch** (114 / 2 / 98 samples, 619 mV, 59.7 W) with no reset. That is
aifoundry3's boot policy reproduced deliberately on another card — but **the mechanism is not the never-exiting
power-down loop** described for 0.20.0 above. At BL2 0.22.0 `check_power_throttle_conditions`
(`services/thermal_pwr_mgmt.c:864-926`) is a **single-pass if/else-if** called once per DM-task pass
(`rtos_task/dm_task.c:267`) whose POWER_DOWN steps one VMIN point and returns; the
`UPPER/LOWER_POWER_THRESHOLD_GUARDBAND` macros are **defined and never used**, so there is no 1.05 × TDP exit
condition anywhere in the tree; and POWER_UP is "always allowed" from any throttle state (`:2267-2270`). At the floor
the firmware's power arm simply has **no step left**, so the **host harness's own power abort is the only guard** —
and the clock is released on the next governor pass when the original TDP is written back. 0.20.0's loop, and
aifoundry3's latch, were read in that older source and are **not** contradicted here; what is gone is the assumption
that one build's mechanism describes the other's. aifoundry3 could in principle be un-pinned the same way, by
writing its TDP back — a different card, needing its own authorization and change record, and its boot service would
re-pin it at the next boot. The power trigger's observed **~1.3 s averaging** is 0.22.0 behaviour (`avg_soc_pwr_mW`),
not 0.20.0's instantaneous reading. The VMIN table has exactly **three** minion points, 600, 700 and 800 MHz, now
published with its parse evidence (E72's `vmin-lut.json`); `DM_CMD_GET_VMIN_LUT` is a safe read (a memcpy out of the
SP's RAM copy, `driver/flashfs.c:2073`), and 🛑 **its sibling SET is a full config-sector erase and must never be
sent.**

**The restore procedure, as it was actually run — follow it.** Read both fields **before** anything is written
(`ettelem config`: TDP, `sw_temperature_c`, power state) and record them in the change record; hold the card lock and
an exclusive window for every launch (`et-who` empty, and no telemetry client holding the single-open management
node); write the originals back after the last run and **read them back in the same session**; run one short burst to
see the governor step normally again; and record the **module's uptime**, which is what proves the restored values
are a real write rather than a reboot's defaults (23 h 29 m at E69's final read, 23 h 46 m at E72's, so the service
processor never reset). Both runs restored aifoundry2 to **TDP 65 W / threshold 65 °C** and were independently
re-read on the card afterwards by another agent (14:58:09 and 15:46:51 PDT), and the card read the same again at
11:04 on 28 October. 🛑 **A card reset would also restore the defaults and must never be used for that**: if a restore
fails or the card stops answering, stop, keep the claim, write it up and alert — do not reset. Two further working
rules this pair produced: **dump the service processor's trace ring per run**, as the knob harness does, because the
only two registered rules E72 could not score in full are exactly the two that needed it; and **never poll the
governor during a measurement pass** — `ettelem`/`gov status` against the single-open management node while a pass
held the card lock produced the one benign kernel line E72 added ("Mgmt: Tried to open same device multiple times").

**🛑 The hazard a raised cap has to pass first: above 65.536 W an affected build's power arm inverts.** A C cast to a
16-bit type **wraps**; it does not saturate. The averaged system power field is 16-bit in units of 10 mW
(`et-trace/include/et-trace/layout.h:467`, so the field itself reaches 655.35 W) and the conversion to milliwatts is
a plain `×10` macro, but on a build whose throttle check narrows the **measured average** (only the average; the TDP
level was already a 32-bit local) to 16-bit milliwatts, **66.0 W reads as 0.464 W**: the throttle-**down** test
(`avg > tdp`) goes false and the throttle-**up** test (`avg < tdp`) goes **true**, so above 65.536 W there is
effectively **no firmware power throttle at all and the power arm pushes the clock up while the card is over its
cap**. In 0.22.0 both locals are 32-bit (`thermal_pwr_mgmt.c:869-871`) and the changelog carries `[SW-22147] Fix
conversion in check_power_throttle_conditions` under *Unreleased*, so **the gate is answered for the card E69 used
and open for every other card until its own build is read**. What still guards an affected build: the **thermal**
arm, which is evaluated first in the same function and is unaffected; and whatever the host harness enforces — in
Q129, an 85 W board-power abort. (This named a third guard, the boot-time PMIC catastrophic power alarm. **Dated note,
Sun 1 Nov 2026 (week 44):** the firmware writes that threshold, and only aifoundry1's card 0 has been seen to act on it
(E84, below). On the other three cards no measurement here shows it acting: treat it as unverified. Host-side aborts
are the guard.) The full reading, with every citation in
the open `et-platform` repository, is
[`../reports/data/2026-10-27-q129-throttle-wrap-gate/`](../reports/data/2026-10-27-q129-throttle-wrap-gate/README.md).
A first pass over the firmware had reported this hazard with the wrong mechanism (saturation), the wrong field (both
operands) and the **wrong direction** (more throttling); all three are corrected there.

**Two card facts this pair added.** 🛑 **Sustained `randn` reaches the mid-80s W on aifoundry2 at its own default
settings**, so an 85 W board bound stops it: both of E69's sustained `randn` cells aborted (85.2 and 85.8 W) and the
return burst at the restored defaults peaked at **86.61 W**, the highest board sample of all 29 reduced runs — E64
had used a 97 W bound, and anything budgeted at 85 W must expect to lose those cells. And **management commands
generate service-processor error events**: E69's count went 6 → 18 (before the first set) → 222 (by the last restore)
→ 234, in 37 bursts following management-command clusters, every one of the 234 being Level Critical / Desc
`SP Runtime Error` / Count 0 / Syndrome "Runtime Error Count Beyond Threshold". None of them indicates a fault from
the governor move, and the abort condition the registration set on them was never met — but a session that counts
these events must expect its own commands to raise them.

**Dated note, Sun 1 Nov 2026 (week 44), Q134: the commands that raise them are residency reads of states the build does not
have.** On BL2 0.22.0 the throttle-residency states are IDLE 0, UP 1, DOWN 2, SAFE 3 (et-platform `836a4ab`,
`device-api/include/management-api/device_mgmt_api_spec.h:280-286`); a read of raw state 4, 5 or 6 fails (rc −5) and logs two
SP ERROR lines, each pushing one `SP Runtime Error` event to the host (E77's F1: its 11 reads of raw 4 raised all 22 events
in its window, each pair 6–8 s after its read). The counter E69 watched is the driver's: of the 1,692 it held on aifoundry2
at 00:13 PDT on 1 Nov, 1,686 are two per committed read of states 4–6 (843 reads) and six, three reads, are in no committed
file; by 19:14:57 PST it held 4,234, of which 4,228 are two per read (2,114 reads); every session that read residency on this
card since its 26 Oct start asked for states 2–6 but E77 (2–4). On aifoundry1's card 0 all 378 are (189 reads). So these
events come from the lab's own residency reads, not from management commands as such. Read states 2 and 3 only. Data:
[`2026-11-01-q134a-alarm-residency`](../reports/data/2026-11-01-q134a-alarm-residency/README.md) (`counters.txt`,
`results.json` › `invalid_state_reads`);
[`2026-11-01-e77-rail-one-temperature`](../reports/data/2026-11-01-e77-rail-one-temperature/README.md) F1.

**A second card's governor moved (aifoundry1's card 0, 1 November 2026, E118; Q133, under the owner's governor OK of
that day).** One TDP write each way, 65 → 0 at 14:52:00.933 PST and 0 → 65 at 15:12:37.217, both `rc 0` and read back,
the threshold never written, the closing read equal to the originals and the module uptime unbroken: no reset, no other
set, and a sampler that sends no PMIC read. The TDP-0 pin held 600 MHz in all 11,182 samples of the pinned passes, as on
aifoundry2, and the service processor's ring logged nothing at all while it was set. The release took **two** "Power
throttle up" events, one per step of the frequency table (600 → 700 → 800 MHz, 0.206 s apart), then 600 MHz at idle, as
every complete ramp in the ring before the pin did. Rule 8, that the two sets write no flash, is PASS for the
version-matched source (et-platform `836a4ab`) and UNKNOWN for the exact running build. Change record:
[`CHANGE-RECORD.md`](../reports/data/2026-11-01-e118-two-clock-card0/CHANGE-RECORD.md). 🛑 **A ring-reading trap it
found:** `tools/claims-v3/dv2/sptrace_events.py` stops at the first binary power-status record, so it saw one
throttle-up where the ring holds two: in the dump after the return burst it stopped at the 16-byte record written 79 ms
after the first throttle-up, and scored one new entry where `tools/claims-v3/hpl/sptrace_full.py` (E64 A1) reads eight,
two of them throttle-ups ([`posthoc_g3_ring.txt`](../reports/data/2026-11-01-e118-two-clock-card0/posthoc_g3_ring.txt)). Count ring
events after an operating-point change with `sptrace_full.py`, by the delta between dumps. How many of the lab's other
committed dumps the old reader under-reads is not counted in any committed file; the published counts of the work that
used it (dv2, dv2v, hp and its copies, `tools/ettelem/analyze_dvfs.py`) were not traced, and the shared decoder was not
edited. E77 moved aifoundry2's TDP the same evening; its corrections after verification were under way when this was
written, and an addendum records it.

**aifoundry2's governor moved twice more (1 November 2026: E77 under Q133, E120 under Q134, both under the owner's governor
OK of that day).** Each wrote the TDP 65 → 0 → 65 and nothing else: E77 at 17:35:34.974 and 17:55:10.848 PST, E120 at
20:55:16.593 and 21:11:41.131, every write read back, the threshold never written, the closing reads 65 W / 65 °C
(`low_power`, 600 MHz idle), and the module uptime unbroken (6 d 3 h 46 m and 6 d 7 h 6 m), so no reset; their samplers sent
no PMIC read, no revisions query and no statistics reset. The pin held 600 MHz again, and after each restore the ring holds
two fresh "Power throttle up" events, 600 → 700 → 800 MHz, as card 0's did in E118. Two working rules they add: a live ring
check must count only entries newer than the previous dump (E77's `run_e77.py` counted every match in the dump, twelve stale
ones included; E120 counted fresh entries only); and a residency read of raw state 4 on this build logs SP errors (E77's F1;
the dated note on E69's events, above). E120's kernel log held no error event in its window. Change records:
[`E77`](../reports/data/2026-11-01-e77-rail-one-temperature/CHANGE-RECORD.md),
[`E120`](../reports/data/2026-11-01-e120-rail-redesign/CHANGE-RECORD.md); results in [03-experiments.md](03-experiments.md),
E77 and E120.

## aifoundry1 card 0's PMIC over-power alarm: a third speed limit (31 October 2026, E84)

E84 ran E80's speed design on aifoundry1's card 0 under its own governor (release 1.4.0 / BL2 0.22.0 / PMIC 1.6.1, TDP
65 W / 65 °C, nothing set) and dumped the service processor's trace ring after every run. In all four fp32 random-data
runs, and in no other run of the 35 or of the smoke, the ring holds lines like
`Pmic_Controller_Handle_Pmic_Error_Event: (step 250 mW) power = 75750 mW, alarm set point = 75000 mW`, the PMIC's power
reading at 75.00–76.25 W (the host driver's counter reads up to 76.75 W, Q132(g)), each followed by a power-status record in throttle state 3 (POWER_SAFE) and
`New OP: Freq 300 MNN 400`. The governor's power arm then climbs back one point a pass, 300 → 600 → 700 → 800 MHz,
because its running average (44–48 W) is far under the 65 W TDP, and at 800 MHz the alarm trips again within 0.1–0.6 s:
a median 1.106 s from one safe state to the next. On the board the same data read 72–75 W at 800 MHz. Over a sustained
run the work samples sit 31–32% at 300 MHz, 32–34% at 600, 25% at 700 and 10–11% at 800, and the kernel's own effective
clock is 0.475–0.479 GHz against a sampled 551 MHz (the gap is not explained; a stall at each of the cycle's four
operating-point changes is one candidate).

- **It is a limit beside the governor's two.** The 65 W power arm and the 65 °C thermal arm never set this 300 MHz point;
  the PMIC's alarm does (the last row of "The clock governor, by firmware build": a real 300 MHz safe state at 0.22.0,
  now *seen*). So on card 0 zeros run 1.67× faster than random fp32 data sustained, against 1.29–1.31× on aifoundry2 the
  same day.
- **aifoundry2 never showed it.** None of aifoundry2's committed trace rings (E80's 64 dumps, E64's 58, E83's 125) holds
  such a line or a 300 MHz operating point, and none of their 93,276 telemetry readings is at 300 MHz, though its fp32
  random data read 80–88 W at 800 MHz. Whether its PMIC (1.5.0), or card 1's (1.3.0), has another set point or raises no
  alarm was not checked.
- **Dated note, Sun 1 Nov 2026 (week 44), Q132(g): aifoundry2 is no longer untested. It does not alarm at any reading it
  reports, on a reading not shown to be card 0's quantity.** The alarm's value comes from the PMIC, and the same kind at
  the same clock reads 5–10 W higher on aifoundry2 with the three rails within about 1 W (a2 ≈ 2.46 + 1.117 × c0), so card
  0's 75 W is about 84–86 W on its reading. It read 85 W or more 654 times in 37 runs (longest 0.8 s), and 75 W or more
  2,907 times in 95 runs, up to 88.88 W; 120,637 readings, none at 300 MHz; 300 rings, no alarm line, though only 23 of
  the runs at 75 W or more have a ring reaching back. The host driver's PMIC event counter reads **0 since its 26 Oct
  boot**, covering 460 of the 654, against **177 on card 0**, all inside E84's four fp32 random-data runs. PMIC 1.6.1
  alarms; PMIC 1.5.0 did not at those readings; **firmware or board, unknown**. aifoundry3 and card 1 never read above
  56.43 and 61.30 W, so they are untested. Not tested on any card: an alarm on the slow average, which the 65 W arm never
  let past 68.91 W; that needs a governor move or a PMIC read. E101 then read 101.15 W on aifoundry2, one held reading on
  three samples, about 88 W on card 0's scale if the same line holds there, and E105 96.25 W. Over nine of that night's
  sessions: 353 rings, no alarm line, no POWER_SAFE record, no 300 MHz point; 164,208 readings, none at 300 MHz, 407 at 85 W
  or more (post hoc, `rings-tonight.txt` in that directory). E84's "hotter per board watt" compares readings on these two
  scales. Data:
  [`2026-11-01-q132-governor-desk`](../reports/data/2026-11-01-q132-governor-desk/README.md) §a.
  **Dated note, Tue 3 Nov 2026 (Q138's records):** card 1 read 62.09 W in E142 and aifoundry3 56.69 W in E144, above the 61.30 and
  56.43 W above, and neither came near card 0's 75 W, so both stay untested; aifoundry2's highest readings that night were 87.95 W
  (E143) and 87.98 W (E144b), under its 88.88 W above.
- **Dated note, Sun 1 Nov 2026 (week 44), Q133: E117, the governor move that would have tested aifoundry2's slow
  average at the PMIC's 75 W set point, was not run.** The desk's NO-GO stands until the owner accepts an outage risk he
  has not yet been asked about: the public source lists an over-power power cycle among the PMIC's reset causes
  (et-platform `836a4ab`, `device-bootloaders/src/ServiceProcessorBL2/include/pmic_hal.h:62`), though no lab card has
  been seen to take that path (card 0 alarmed 177 times and stayed up; aifoundry2 read up to 101.15 W and stayed up).
  On card 0 the same day, E114 found that **the firmware-revisions query is a PMIC command**: at `836a4ab` it writes the
  PMIC's firmware-management command register twice (E114 C1). Take a card's identity by uptime continuity, as E118 and
  E77 did. E114's 51 reads of throttle residency states 4–6 (rc −5) leave the service processor's "Unexpected power
  throtlling state" lines in card 0's ring. Card 0's kernel log counted 575 error events at 00:13 PDT and 701 at
  14:50:39 PST, and none was added through E118, whose sampler sends no PMIC read; by their timestamps E118 places 120
  of them in E114's session (the stock sampler), which E114, reading no kernel log, leaves open: the stock sampler's
  voltage-register reads or that session's heavier load would fit. Data: [`2026-11-01-e114-card0-replicates`](../reports/data/2026-11-01-e114-card0-replicates/README.md) C1, C8;
  [`2026-11-01-e118-two-clock-card0`](../reports/data/2026-11-01-e118-two-clock-card0/README.md).
- **Dated note, Mon 2 Nov 2026 (week 45), Q134's records, after their verification, on the note above:** "an outage risk
  he has not yet been asked about" did not hold: the session had put E117's outage risk to the owner at 16:04 PST on 1
  November, before that note was written, and put it again at 18:57 (the [Horace
  hub](https://spacesheep.dev/@yaroslavvb/horace-hub)'s record). E117 stays not run, awaiting his acceptance.
- **Dated note, Sun 1 Nov 2026 (week 44), Q134(a): since it started on 26 Oct, aifoundry2's service processor has not entered
  POWER_SAFE.** Raw throttle-residency state 3 read 0 µs at all 712 committed reads, from 11 sessions (E69, 27 Oct 14:20:45
  PDT, to E77, 1 Nov 17:59:25 PST), while raw 2 rose monotonically from 1,095.9 to 4,717.6 s under one service-processor
  lifetime; the driver counts 0 PMIC events (Q132(g)'s zero, carried to 19:14:57 PST) and 0 throttle-time events. On card 0,
  the positive control on the same reported release (BL2 0.22.0; PMIC 1.6.1), the counter is an exact record of the alarm:
  the kernel log's 146 THROTTLE_TIME durations, replayed through the bookkeeping of a public tree that declares 0.22.0
  (et-platform `836a4ab`), reproduce all 63 committed raw-3 reads on all four fields; 177 alarm interrupts made 146 episodes
  of 0.284–0.462 s, 60.003 s in all, only in E84's four fp32 random-data runs, 36–37% of each sustained run. aifoundry2's
  zeros cover readings up to 101.15 W (456,199 readings, each sample once, from 15 of its 16 card sessions since the start;
  the PMIC's own average peaked at 71.85 W). So no PMIC over-power (or over-temperature) interrupt has reached aifoundry2's
  service processor in that lifetime. Not settled: an alarm on the slow average or any filtered quantity (the 65 W governor
  never let the average reach 75 W), whether its PMIC raises the line at all (firmware or board), the build hash and the set
  point. Three side facts: the driver's "Thermal Throttling Duration … msec" is microseconds (the host-clock lag shows it);
  the statistics reset leaves the residency counters alone (in source, and raw 2 unchanged across E85's 2,205 resets); and
  raw-state numbers depend on the build (POWER_SAFE is raw 5 on 0.18.0 and 0.20.0). **And E114's open events are its own
  residency reads:** card 0's 126 events between 00:13 PDT and 14:50:39 PST, the 120 that E118's timestamps place in E114's
  session among them, are E114's 21 committed reads (17 in its session, 4 in its smoke) × 3 invalid states × 2; the "51 reads
  of states 4–6" above counts the session's only, and neither the stock sampler's voltage-register reads nor the load is
  needed. Data: [`2026-11-01-q134a-alarm-residency`](../reports/data/2026-11-01-q134a-alarm-residency/README.md).
- **For a run on card 0:** expect fp32 random data at 800 MHz to cycle through 300 MHz, and register a label and a stop
  or a count for the alarm (E84's labels had no PMIC category, so its limit rule scored the alarm runs as misses); Q130's
  evening round left card 0 out for this reason. 30 of E60's 33 300 MHz episodes on this card (20 October) match the
  alarm cycle, but E60's rings were not committed, so the alarm is not confirmed for that date.

Data: `docs/reports/data/2026-10-31-e84-speed-aifoundry1-card0/posthoc/pmic.{json,txt}` and that README's post-hoc
section (labelled post hoc, never a verdict).

## A one-second idle reset inside a launch (aifoundry2, 23 October 2026, E63)

E63 ran one 8.5 s heater launch per 10 s phase, each after a ~1 s idle gap, on 256 and then 192 minions (about
34–42 W on the board, die 54–57 °C, PMIC 54–57 °C). In 8 of its 360 launches (4 in each session, in the top-rung and null blocks) the
clock fell from 800 MHz straight to the boot point, 600 MHz, for 0.6–1.5 s and climbed back through 700 MHz, the SRAM rail
stepping 830 → 704 mV with it, anywhere from 1.4 to 8.4 s into the launch (the first session's four all at 7.2–7.3 s);
the board power fell by 9–12 W while it lasted, and the sampler's command took 38–132 ms at its onset against a median
of 22. The heater's own internal launches ran on without a gap over 2 ms, and its cycle counters read 0.60 GHz through each
dip, so the work continued at the lower clock. It is not the thermal loop (the die read 54–57 °C, against 65) and not the
power test: the six dips the sampler caught a reading for started at 34.1–41.6 W, against the firmware's 65 W TDP,
and the other two have no reading (corrected 26 Oct 2026 from "36–42 W", which three of the six are under).
Its shape is the governor's idle reset and climb (above: launch to
800 MHz a median 0.67 s, at most 1.2 s), as if the service processor saw the card idle for an instant. That reading was
right; this section said "why it fires mid-launch is not known" until 1 November 2026 (next paragraph). E62's back-to-back
launches showed nothing like it. For a power measurement: allow for a ~1 s step to 600 MHz in about one launch in 45 when
launches follow idle gaps, or read the clock per sample, as E60's amendment A2 window does. Data:
`docs/reports/data/2026-10-23-e63-camera-hamming-ladder/s*/dips.json`.

**What fires it (Sun 1 Nov 2026, week 44; E100 and Q132(g): a registered test on one card and one kind, with a matching
public source, not shown in the card's binary).** A check once a second on the card's clock reads idle in the gap between
two kernels, and sends the clock to 600 MHz until the next check. In public source at et-platform `836a4ab` that is the
Master Minion's heartbeat: it sends a snapshot of that instant, busy only if a kernel slot reads `KERNEL_STATE_IN_USE`
(`device-minion-runtime/src/MasterMinion/src/services/sp_iface.c:76-100`, `workers/kw.c:1915-1930`); the SP passes it on
(`rtos_task/command_dispatcher.c:476`) and on any busy-to-idle edge notifies POWER_IDLE at once, with no debounce
(`services/thermal_pwr_mgmt.c:3110-3124`), which sets the boot point (`:2177-2180`); the power branch climbs only while the
state is not idle (`:879-880`, `:910-919`). So a launch's *internal* kernel boundaries count, not just a host's idle gap.
- **Tested from outside.** On aifoundry2, int8 zeros at about 35 W, falls per about 146 heartbeats at 800 MHz: 3, 3, 10 and
  33 at added gaps of 0, 5, 20 and 100 ms, each inside its frozen band, and 0 in 126 heartbeats inside 50 kernels of about
  4 s. A lattice fitted on one round predicted the other: **39 of 39 heartbeats in a gap fell, 0 of 234 inside a kernel**
  (234 is one tied lattice's count). All 61 falls first read −1.9 to +117.9 ms from the other round's lattice point. All
  five rules passed.
- **What it costs:** a fall lasts one heartbeat, a median 1.10 s at 600 MHz, about 0.3 s of full-speed work. The climb's
  "launch to 800 MHz a median 0.67 s" above is the first heartbeat inside a kernel plus about 0.3 s.
- **How often:** about 1 in 500 kernel boundaries with the sparsity host's stock launches, post hoc over 25 falls in six
  sessions, with no dependence visible on die, power, format or session position. E100's own no-gap arm, 1 in 152 at
  800 MHz, 95% about 1 in 52 to 1 in 735, is compatible and adds no further support. Runs on a fixed grid (E63, E73, E85)
  hold one phase against the heartbeat, so they pile up at one time in the process. A sustained run's count can miss them:
  E105's `gemmc1-int8-zeros` read 786 MHz through 9 dips of 1.2–1.3 s, 6 at process boundaries, which `idle_resets_sus`
  mostly does not count.
- **What it does not show.** That the check is that heartbeat is read from source and tested from outside; any other
  once-a-second card-side check reading the same state would look the same. The cards report minions 0.25.1 against a
  public changelog at 0.24.0 plus unreleased, and the binary was not read. One card, one kind. N's 0 of 126 alone does not
  separate a long kernel from no added gap (Fisher p 0.25), so "a long kernel avoids them" rests on the lattice table.
  Data: [`2026-11-01-e100-idle-reset`](../reports/data/2026-11-01-e100-idle-reset/README.md),
  [`2026-11-01-q132-governor-desk`](../reports/data/2026-11-01-q132-governor-desk/README.md) §b.

**On a second card (aifoundry1's card 0, 1 November 2026, E114, post hoc).** In 135 launch processes the same check
dropped the clock to 600 MHz in a third of the 0.33 s gaps between processes: Q132(g)'s heartbeat lattice, fitted on
the session's five falls inside processes (a period of 1000.0191 ms; E84's 1000.0186), predicts 95 of 95 gaps, 31 of
which fell. 40 of 120 later starts climbed (13 of 40 in E84), every first start climbs, and the climb ends 0.39 ± 0.05 s
after the first heartbeat inside a kernel. So **at the 800 MHz cap a 40 s window's count of falls decides about ±1% of a
cell**: card 0's int8 zeros read 0.8% slower than random int8 in E114 and 0.8% faster in E84, a fall more or fewer per
window, not a property of the data. Data: [`2026-11-01-e114-card0-replicates`](../reports/data/2026-11-01-e114-card0-replicates/README.md) §3, `posthoc/`.

**E85's "possible trigger", which gives way to the above (31 October 2026, post hoc; dated note, 1 November).** E100 saw
no rise in falls with the statistics reset (12 against 10, Fisher p 0.83, both inside one band), and its falls sit on the
heartbeat's lattice with the reset's phase anywhere. The reset can delay the service processor by about 100 ms: two falls
first read about 105 and 118 ms after a lattice point in a gap, each right at a reset, n = 2. E85's own text: its sampler,
inherited from E63's runner,
sent the card a statistics reset once a second (`--reset-ms 1000`; the telemetry table, below), and each reset call held
the sampler about 121 ms against its 78 ms sleep. Late clock ramps fell in 13 of the 47 launches whose 1.5 s check sample
came right after a reset, against 10 of the other 193 (one-sided Fisher p 3.5 × 10⁻⁵), and 4 of E85's 6 mid-launch
idle-reset dips began right after a reset (P 0.012, in a window chosen after the data); at all six the sampler's command
took 42–134 ms against a median of 22, as at E63's dips, whose sessions ran the same flag. So a reset may delay the SP's
governor pass. E64's, E78's and E80's runners sample without it, as E86–E91 did. Data: `docs/reports/data/2026-10-31-e85-camera-kinds/corrections-check.txt` [C9].

## A hot start does not hold the clock down, and a real kernel can read over 100 W (aifoundry2, 1 November 2026, E101)

E101's speed session chose a start heated to the 65 °C trip for the cells above the limit, on the assumption that a die
at the trip holds the clock low. It does not. Under the resident heater at the trip the clock cycled 600–700–800–700–600
MHz about once a second, the board 53–67–87–68 W, and the work met that cycle on a rising edge. `mm16`, the benchmark's
loop, on fp16 random, read **101.15 W** on the board on three samples, one held PMIC reading, at 700 MHz, over the
registered 97 W stop: the session ended at run 82 of 96. Earlier in that session `mm16` on int8 random read 90.07 W from a
cool start; 88.88 W had been this card's highest working reading before that night. **So budget a real kernel's random
data past 100 W on this card's board, keep a board stop on it, and never count on a hot die to slow it.** The resident
loop's numbers do not bound a streaming kernel's: int8's benchmark runs +17.45 ± 0.14 W over its resident loop at 600 MHz on
aifoundry3 (R4). Data: [`2026-11-01-e101-real-matmul`](../reports/data/2026-11-01-e101-real-matmul/README.md), session 2,
`aifoundry2/s1/tel/`.

**The power rule that failed, and its future form (E105, the same morning).** E105's GEMM pattern with B packed by column, whose
tiles fit the L2, reads as high from a cool start at 800 MHz. Its rule estimated a cell from a lower-power probe of the same layout
and format (rho) and admitted it at 88 W or under: by-column random fp32, estimated 87.83 W (rho 0.81; the true share 0.90), read
95.2 W at 800 MHz and peaked at **96.25 W, 0.75 W under the session's 97 W stop**. The 93 W lock then refused its sustained run; fp16
random went on under the lock and read 91.91 W in the burst and 94.32 W sustained, on a hot die. The estimate ran 3.2–8.4 W under
the reading on 19 of 63 runs, the high-power cells. 🛑 **So sustained random fp32 by column sits at this card's stop: about 98.7 W, an
extrapolation, and it could not be expected to complete under the 97 W stop. Its refusal is not a gap to fill by rerunning. The
rule's future form: estimate from the same kind's S on a pinned card (E105's P4 read 94.6 W against 95.2 W, and aifoundry3 had that
S before the burst ran), never from a lower kind's rho, and lock by layout and format.** Two readings to carry with it. Only 600
and 800 MHz held for a whole launch, on every layout, so a slope of T on the clock is a line through two points. And the sampled clock
reads the governor's hunt high, so a rate gap can print above its clock gap, which the law forbids: use the kernel's own clock,
cycles_max ÷ wall. Data: [`2026-11-01-e105-gemm-layout`](../reports/data/2026-11-01-e105-gemm-layout/README.md), "The power rule did
not do what it was for", `aifoundry2/admission.json`, `aifoundry2/s1/skipped.jsonl`.

**A large GEMM that streams to DRAM never meets the governor (E136, 2 November 2026).** On aifoundry2 under its own 65 W / 65 °C governor, a 4,096³ fp32 GEMM in the vendor's pattern (192 MB with C) ran random data at 800.0 MHz sustained, 57.5 W on the board and a 63.3 °C die, so zeros and random ran at one speed (×0.995 sustained): the memory path holds it to 3.86 TFLOPS, too slow for random's power to reach the limit. The 20 MB GEMM the L3 holds is the one the governor caught: random fp32 at 656.3 MHz sustained, 55.2 W and 65.7 °C, its burst 62–70 W, and the session's highest board reading 76.09 W. Data: [`2026-11-02-e136-large-gemm`](../reports/data/2026-11-02-e136-large-gemm/README.md), `results.json` `cells`.

**Under aifoundry2's governor the power limit can act before the trip, and a burst can settle either way (E143, E144b, E146; 2 November 2026).** In E144b's 15-minute hold of random fp32 the power limit stepped the clock down 2.3 s after the first process started (the SP's running average 65.5 W against the 65 W TDP, the die at 52 °C), well before the die's first reading of 66 °C, and the clock kept leaving the 600 MHz floor until 70 s after it; the board peaked at 87.98 W, none over 90 W, as in E111 and E133. In E143's 6 s bursts of new kinds, random-like fp32 settled at 694–724 MHz and random-like fp16 at 721–731 MHz while every int8 tile stayed at 796–800; one gated fp32 tile (`fp32.wideexp48_bgate_alt`) ran one pass at 754 MHz and 58.2 W with no power-down event and its other two at 795.8 MHz, and two int8 tiles each ran one pass at 784–788 MHz; the kernel's own clock read 12–18 MHz below the sampled clock on governed tiles, and the governed clock read 4.96 MHz below M7's prediction, about the 8.0 and 7.6 MHz E80's own random tiles had drifted since 31 October (E143's R0). In E146 a fresh 3,072 × 2,048 × 3,072 fp32 GEMM reached the 65 °C trip with random data and the governor held it at 745 MHz. Data: [`2026-11-02-e143-blind5-aifoundry2`](../reports/data/2026-11-02-e143-blind5-aifoundry2/README.md), [`2026-11-02-e144-heat-minutes-aifoundry2`](../reports/data/2026-11-02-e144-heat-minutes-aifoundry2/README.md) C3, [`2026-11-02-e146-gemm-stores`](../reports/data/2026-11-02-e146-gemm-stores/README.md).

**Under aifoundry2's governor its dips are its own, the session moves the clock, and process starts step it (E158–E161, Q139(u), Q139(s); 3 November 2026).** E82 A2's "dips" are not the meter's on this card but the governor's own low-voltage phases: in E143, 98.4% of the 449 dips at 55 W or more fall within ±2 samples of a clock and set-point change (36.8% of the other samples), and matched to kept samples at the same service-processor clock and voltage reading they read −0.03 W from them, where the 600 MHz cards' dips read 7.8–11.0 W below theirs; so aifoundry2's committed dips-kept reduction is its footing (Q139(u) C1). The die reads 518, 567–569 and 618 mV at 600, 700 and 800 MHz against set points of 520, 570 and 620, 700 MHz being a transit point, and hot runs read up to 2 mV low; the service processor's minion-rail voltage statistic lags each step, so read the voltage from `die_mv` or `reg_mv` (Q139(s)). The service processor logged a mid-burst idle status in 3 of E160's 150 bursts (1 of E143's 117), and each of those passes ran slow: the fp16 zeros anchor at 752 MHz where its other passes held 800, `fp16.c_absorbed` at 732.7 against 757–758, `int8.bflip_bit5_w` at 756.9 against 800 (E160 C1). From one session to the next the same tile can run faster at the same power: E80's fp16 random tile ran 10.74 MHz faster in E160 than in E143 at +0.06 W, the die starting each burst 1.7 °C cooler on average (53.69 against 55.43 °C), with the host binary changed too, so session and host are not separated; the capped tiles held 66.72 W (E143 66.89 W), above M8's refitted 65.20 W cap (E160 C7). In a large GEMM hold the governor does not hold, the clock still dips to 600–700 MHz, mostly 0.2–0.3 s into a process and sometimes mid-process (8.5% of E159 H1's window), and at a steady 800 MHz the board rises 0.49–0.50 W per °C of die (E159 H1, 47 → 64 °C); about 3 W (2.1–4.0) of that 46 °C cold start's 7.2 W first-second deficit against P0 is the start die, every burst behind P0 having started at 47–56 °C (E159 C1, C2). In E161's G2Q the clock fell to 600 MHz at the start of the second process (8.5–9.6 s, the board down to 38 W, the die 53–54 °C), the kind of process-boundary step E144b's G1 had shown; M8's 65.2 W cap, from which it predicted G2Q's first step down at 48 s, never bound (the highest board sample in the first 60 s was 64.9 W), and the trip regime followed the die's first 65 °C at about 56 s. The hottest-sensor field read a held 70 °C, the service processor's running maximum, at every sample of E158, E159, E160 and E161. Data: [`2026-11-03-q139u-footing`](../reports/data/2026-11-03-q139u-footing/README.md) C1, [`2026-11-03-q139s-clock-voltage`](../reports/data/2026-11-03-q139s-clock-voltage/README.md), [`2026-11-03-e159-gemm-sustained`](../reports/data/2026-11-03-e159-gemm-sustained/README.md) C1–C2, [`2026-11-03-e160-blind6-aifoundry2`](../reports/data/2026-11-03-e160-blind6-aifoundry2/README.md) C1, C7, [`2026-11-03-e161-heat-e2e-aifoundry2`](../reports/data/2026-11-03-e161-heat-e2e-aifoundry2/README.md).

## The heat path moves with the hour and the day, and a hold settles slowly (1 November 2026; Q132(g), E98 on aifoundry2, E97 on aifoundry3)

- **The rest die cycles by about 3.5 °C a day.** Nine days of the boxes' own 5 s history: aifoundry2 at rest reads 46.1 °C at
  11:00 PDT and 49.6 °C at 20:00 PDT, and the other boxes follow it at r 0.90–0.95. So compare a sustained speed near
  the trip at the same hour, or read the rest die beside it.
- **The die line's height moves with how warm the card idles.** On one night of aifoundry2 the warmest of four probes sat
  0.46 °C above the other three for 0.88 °C of idle die; one contrast, cause not measured. Post hoc over four sessions the
  line moves about 0.25–0.35 °C per °C of rest die, 95% roughly 0–0.6, and E98's registered reading is 0.50 [0.31, 0.70], so
  quote none of these as a rate. Whether the rest die accounts for the 3 W at the trip between 23 and 31 October is not
  shown: every session that says so is measured against E64. No inlet was read, and the fans are unread.
- **What the night showed.** By morning the card idled about 1 °C cooler, and a card on another box that never ran fell by
  about as much. A held 41 W load read 2 °C hotter on the warm probe, which cannot tell the room from the heat path.
  Hosts' NIC and NVMe sensors are a free, coarse stand-in for an inlet reading, not a calibrated one.
- **A hold settles at about 0.9 °C per board watt on aifoundry3, and that is a plateau, not a steady state** (E97, three
  single holds, one session). The registered steadiness test failed on two of three, and the plateau moved three times in
  about an hour by 0.3–0.8 °C, uniformly across the sensors, cause not established (at the second, aifoundry2's idle reading
  moved +1.21 °C inside E98's P6 rest window and was back by 05:50 PST: E98's dated note). On the die's own sensors 45% of the rise
  arrives by 60 s and 90% by 5 minutes; E73's 95% in 49 s is the camera on the back of another card. About a third of the
  board's rise over idle is the idle power's climb with temperature, and the loop gain works out to about 0.4 at the trip's
  temperature on this card (derived). The lab model's 1.47 °C/W is aifoundry2's September fit, not this card's, and nobody
  has measured aifoundry2's steady coefficient since October's cooling change. A rest to within 0.1 °C takes about 9 minutes
  on this card after rises of 7–20 °C. Random fp32 at full duty reaches the lab's 78 °C stop 221 s from rest, with no
  measured plateau below it.
- **aifoundry2's coefficient since October's cooling change is about 0.67 °C per board W, and random fp32 at full duty
  plateaus there** (dated note, Sun 1 Nov 2026, Q133, E111). Two holds: 0.672 (range 0.647–0.696) on int8 `neg_ones` at
  18.6 W over idle, from rest, and 0.671 (range 0.651–0.685) on random fp32 at the 600 MHz floor at 32.4 W over idle,
  linear between them; random fp32 settles at **67.3 °C at 54.2 W**. Not a steady state by the registered test either:
  the die wandered about 1 °C after reaching its level, cause not established. aifoundry3's random fp32 at the same
  600 MHz drew about 40 W over idle and was still climbing at the 78 °C stop (E97): the two cards differ in power and
  cooling, not in the governor. No warm probe was possible that afternoon (idle 21.7–21.95 W); W2, a cool probe, falls on
  E98's line, post hoc. Data: [`2026-11-01-e111-heat-steady`](../reports/data/2026-11-01-e111-heat-steady/README.md).
- **A second card's die line moved too** (E114, aifoundry1's card 0): 1.67 °C cooler (about ±0.5) at the same board
  power between the afternoons of 31 October and 1 November (1 Nov 39.36 + 0.4941 °C per W; 31 Oct 41.78 + 0.4753),
  with its rest die lower; random fp16, at the trip, ran 3.3% faster for it. No inlet was read. Data: [`2026-11-01-e114-card0-replicates`](../reports/data/2026-11-01-e114-card0-replicates/README.md) §4.
- **A governed sustained cell did not replicate between two sessions** (dated note, Mon 2 Nov 2026, Q136, E126; aifoundry2).
  In a second session of E119's four sustained fp32 pairs what the clock buys repeated to within 0.002, but random's governed
  clock ran 37–83 MHz faster (`c8s` 663.7 → 746.5 MHz), so zeros' lead fell from ×1.229 / 1.148 / 1.062 / 1.079 to ×1.189 /
  1.088 / 1.025 / 1.023. By proxies only: the card idled at 43 °C / 21.26 W against 46 °C / 21.92 W before E119's, the random
  runs drew 4.55–8.76 W more, and the block came earlier in the session, so every random run reached 65 °C 15–36 s later and
  its 40 s window sat earlier in the warm-up. Give a governed sustained gap its session, the idle before it and its start
  temperature. Data: [`2026-11-02-e126-gemm-arms`](../reports/data/2026-11-02-e126-gemm-arms/README.md) §5b.
- **aifoundry2's coefficient has a replicate** (dated note, Mon 2 Nov 2026, Q136, E133; its data README's registered reading,
  which no verifier had read when this was written). In a second session per kind the holds read 0.648 (fp32 random) and 0.700
  °C per board W (int8 −1s), 0.65–0.70 over four holds in two sessions; neither steady by the registered test. A 1 °C cooler
  idle (44.0 °C) put random fp32 at the governor's trip, not its floor, and one cool probe put the 76 s line at 0.81 °C per °C
  of rest die. Data: [`2026-11-02-e133-heat-holds`](../reports/data/2026-11-02-e133-heat-holds/README.md). **Verified** (dated
  note, Mon 2 Nov 2026, E133's addendum): holds with fixes (`f50c77fd`). Per kind: by R1 fp32 random's coefficient replicates
  (PASS 0.966, Sunday's hold at the floor against Monday's at the trip) and int8 −1s's is INCONCLUSIVE (1.042 [1.005, 1.111]).
  The card fact: **aifoundry2's governor steps the clock down at a whole-degree reading of 66 against its 65 °C threshold** (the
  integer mean of the minion sensors; all 20 distinct SP throttle-down events in E133 read 66 against 65), so a floor plateau
  that reads 65 releases the clock and the die pins at the 65/66 boundary.
- **Heat over minutes, scored blind** (dated note, Tue 3 Nov 2026, Q138's records; E144 on aifoundry3, E144b on aifoundry2). On
  aifoundry3, one session in a steady room (rest die 51.2–51.6 °C), Q138(t)'s frozen five-stage chain followed the die through two
  13-minute holds to 0.18 and 0.04 °C rms given the board's watts, and put the plateaus within 0.15 °C from the planned power; the
  warming die's leakage was 25–30% of the board's rise. Item 8's like for like, E97's H3 against E144's H_H, read −1.0% per board
  W from 1 to 2 November, consistent with no drift, with no inlet reading to tell room from path. On aifoundry2 the rest die read
  a whole 46 °C in every sample of both rests, so every heat verdict there carries ±0.5 °C of anchor; int8 −1s at 800 MHz ran
  0.71–0.73 °C above the chain's single coefficient at each hold's end in all three sessions (E111, E133, E144b), which does not
  yet say format matters: clock, voltage, watts and governor state differ too (E144b C1). Data:
  [`2026-11-02-e144-heat-minutes`](../reports/data/2026-11-02-e144-heat-minutes/README.md),
  [`2026-11-02-e144-heat-minutes-aifoundry2`](../reports/data/2026-11-02-e144-heat-minutes-aifoundry2/README.md).
- **Heat over minutes predicted from the bits** (dated note, Tue 3 Nov 2026, Q139's records; E154 on aifoundry3, E161 on
  aifoundry2). On aifoundry3, R0's rest die read 51.41 °C; every pool-6 hold started on a tail of 1.89–4.43 °C carried from the
  hold before; given the board's watts Q138(t)'s chain read the three 11–12 °C rises 3.1–4.6% low, int8's H_M among them, and the
  two small int8 rises within 0.07 °C, where E144 had read a 15.0 °C rise to +0.015 °C on 2 November, so the 3–5% belongs to this
  session, cause not established (no inlet reading); E97's H1, held a third time, rose 0.884 °C per board W at 600 s, 0.984 of
  E97's 0.898. K_S's duty-cycled peak read 67.54 °C, 0.04 °C over its design line and 4.5 °C under the 72 °C hold stop (E154 C2,
  C4). On aifoundry2 both of E161's rests read a whole 47.0 °C in all 1,199 samples (22.12 and 22.19 W), so its verdicts carry
  ±0.5 °C of anchor, over which G1Q's plateau error runs −0.19 to −1.61 °C. Data:
  [`2026-11-03-e154-heat-e2e-aifoundry3`](../reports/data/2026-11-03-e154-heat-e2e-aifoundry3/README.md),
  [`2026-11-03-e161-heat-e2e-aifoundry2`](../reports/data/2026-11-03-e161-heat-e2e-aifoundry2/README.md).

Data: [`2026-11-01-q132-governor-desk`](../reports/data/2026-11-01-q132-governor-desk/README.md) §c,
[`2026-11-01-e98-heat-path-drift`](../reports/data/2026-11-01-e98-heat-path-drift/README.md),
[`2026-11-01-e97-heat-low-power-steady`](../reports/data/2026-11-01-e97-heat-low-power-steady/README.md).

## Nothing limits the die's temperature (aifoundry2, aifoundry3, aifoundry1's card 1)

**Dated note, Sun 1 Nov 2026 (week 44):** what follows reads what the firmware writes, not what a PMIC does with it. Only
aifoundry1's card 0 has been seen to act on a PMIC alarm, the 75 W power alarm (E84). On aifoundry2, aifoundry3 and
aifoundry1's card 1 no measurement here shows a power or temperature alarm acting: treat it as unverified, and take
host-side aborts as the guard.

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
- **An idle runaway meets nothing either.** On BL2 0.20.0 (release 1.3.1, aifoundry2's card) the thermal test acts busy
  or idle ("The clock governor, by firmware build", below), but its only response is one point down the VMIN table, and
  the idle card already sits at the lowest point (600 MHz), so the loop changes nothing. The PMIC alarm's safe state
  sets the frequency register but not the PLL: `go_to_safe_state()` (at `ffca4cbb4`) moves the PLL only when its
  voltage lookup fails, and its voltage update is commented out (fixed upstream in `e024210bc`, 5 September 2024).
  `pmic_force_shutdown()` is defined and never called. In the current upstream code (`836a4ab`,
  `check_power_throttle_conditions()`, `thermal_pwr_mgmt.c:864–883`) the thermal test does not run at all while the
  master minion is idle. aifoundry2's idle card reached a 138 °C mean (hottest sensor 144 °C) at 133–134 W on 2 and on
  7 October, and dropped off the PCIe bus both times. (Read from source on 7 October
  2026.)
- **The one possible exception is aifoundry1's card 0** (then recorded as release 1.4.1, not in the campaign): it read
  115–117 °C after its smoke blocks of 25 September before it dropped to 300 MHz (the section on that card below);
  whether its PMIC's safe state or 1.4.1's idle point did that is not established. (Its PMIC does drive a 300 MHz safe
  state: E84 saw the over-power alarm do it on 31 October, above.)

The only guard is the runners' own cap: stop at a mean of 90 °C (`tools/ettelem/run_horace_long.sh`, the DV2 watcher).
A runner that holds a temperature needs an upper stop too; the version-3 catalogue runner
(`tools/claims-v3/cat/run_catalogue_t10.py`) has none. The counts here: `python3 tools/claims-v3/dv2/recount_v3.py
over90` (every telemetry file whose mean passed 90 °C), `… pass` (catalogue pass 11), `… systemc` (`sp.system_c`) and
`… cool-busy` (aifoundry1's card 1, above), each over the three-card check's passes only (E48's `gs/` passes, filed in the
same tree, come in with `--with-gs`), so they equal the DVFS page's counts (`dvfs.json` `v3.sp_readouts`).

## Setting a rail's voltage: two firmware hazards (read from source for E54, 28 September)

NV (E54) sets the mesh (NoC) rail with `DM_CMD_SET_MODULE_VOLTAGE`. Reading that command's path in each build the cards
run found two hazards; neither has been triggered on a card, since no voltage has been written yet.

- **BL2 0.18.0 writes every NoC voltage set to flash** (release 1.2.0: aifoundry1's card 1 as recorded until 31 Oct
  2026, when it read BL2 0.22.0, E82 A1; whose voltage path was not read, so read the exact build before any set). Its
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
| `board_w` | board power, 10 mW steps | refreshed once per service-processor pass, and a poller lengthens the pass: under ettelem at 10 Hz a new value every 156 ms on aifoundry2, 158 on aifoundry1's card 1 and 263 on aifoundry3; with nothing polling the pass is 133, 135 and 224 ms (E41, 26 September); near-instantaneous otherwise. 🛑 **It can read a launch gap:** on aifoundry1's card 1 (E82) and on aifoundry3 (E78, E81, E86, E90) a reading sometimes lands in the 1–2 ms gap between two launches and is then held for one pass — one or two samples 4–20 W low, 12–151 ms after a launch boundary, with the minion rail unmoved (E82: 85 samples in 61 events over seven passes; E86: 13 in power windows over five passes, 1–7 a pass in E78's). One dip pair in a 20-sample window lowers a run's mean by 0.4–1.2 W, and the registered gates have set passes aside for them (E82, E86): remove them by E82 amendment A2's rule (`board_w[i] < min(board_w[i−2], board_w[i+2]) − 4.0 W`) or register a gate. On aifoundry3 they are routine (1 November 2026): E92 39 dips, 22 in power windows, which made seven of its ten rules INCONCLUSIVE, mostly on interval width, and moved every fp16 contrast over `c_abs` by 0.3–0.5 W; E95 60, 17 in windows; E99 112, 21 in windows. E78's random-anchor gate set E92's 9211 and E95's 9513 aside on them |
| `sp.minion_w`, `sram_w`, `noc_w` | per-rail power | **the PMIC's running average, first-order, published one SP pass late** (E58, pre-registered): τ minion 1.06 s, SRAM 1.01, NoC 1.04 on aifoundry3; minion 1.08 and NoC 1.08 on aifoundry1's card 1, but **its SRAM rail 0.54 s**, so the cards' SRAM meters differ. (E27's single-parameter τ ≈ 1.15–1.22 s folded the SP's pass into τ; a step reaches 55–57% after 1 s and 83–84% after 2 s as read.) The published rail split (the last 0.6 s of a burst, divided by 0.94) assumes τ near 1.1 s: on the catalogue's 3.2 s bursts it errs by −1.8 to −4.3% on every rail but card 1's SRAM rail, where it errs by +5.5% (offline, `tools/claims-v3/tau/PREREG.md`). `tools/ettelem/deconv.py` undoes the filter with each card's τ (a burst's energy within 0.3% of the step on aifoundry3). The SP copies the reading each pass (so on aifoundry3 the copy changes only every 263 ms under ettelem); not a moving average. Skip 2–3 s after any change before averaging. `ettelem sample --reset-ms` resets the statistics on a schedule, and the reset also restarts the running average: with a reset every second, one second after a burst the rail has fallen 93% of the way on every card (E41). 🛑 **The reset is a PMIC command:** it is `DM_CMD_SET_STATS_RUN_CONTROL`, which the SP forwards to the PMIC as the PMIC's own statistics reset (0x47; `tools/ettelem/ettelem.cpp`, `resetStats`). E85 sent it 2,205 times in one session (its C1), as E52's, E62's, E63's and E73's samplers had sent it before, and its control word switches the SP's statistics trace off (`tools/claims-v3/tel/README.md`, deviation 1); whether E85's resets, or E100's arm R, left aifoundry2's trace off has not been read on the card. **Allowed by the owner's ruling of 31 October 2026** (AGENT.md §5); E64's, E78's and E80's runners sample without it |
| `temp_c.minshire[0]` | die temperature | **whole degrees**, and it is the *integer mean of 34 shire sensors, each truncated to a whole degree*, so it reads about 1 °C below the mean of the same sensors' readings (E89). Hot spots are hotter. On aifoundry3's firmware build each sensor's raw 12-bit code can be read ("The sensor reads whole degrees", below) |
| `temp_c.pmic` | **not the PMIC's temperature** (dated, Mon 2 Nov 2026, Q136's records) | at et-platform `836a4ab` the telemetry fills it from the minion shires' PVT average (`thermal_pwr_mgmt.c:732`), so it equals `minshire[0]` in 16,149 of E127's 16,155 samples (E127 C5); no telemetry field reads the PMIC's own temperature, which its 75 °C alarm compares (E128 C6). A stop on it is a die stop: register a board-power stop under 75 W beside it |
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
- **The memory shires' DDR die rail moves in whole-millivolt steps** (E110, 1 November 2026): a 0.14 W step read
  −0.08 mV and a 0.36 W step −1.01 mV, so a registered bound must not assume a linear reading (E110's D2). It moves with
  the DRAM read path's 64-bit toggles and not with its 256-bit path, so it can place a step on or off the memory shires'
  logic. Data: [`2026-11-01-e110-memory-width`](../reports/data/2026-11-01-e110-memory-width/README.md).
- Finer voltage exists: raising the SP log level to DEBUG and extracting the trace gives a **per-shire** on-die
  voltage map (E6). Restore the log level afterwards.
- 🛑 **The stock telemetry reads PMIC registers, and one identity query writes one** (dated, Sun 1 Nov 2026, Q134's records).
  `ettelem config` sends `GET_ASIC_VOLTAGE` (two PMIC voltage-register reads a call), and each `ettelem sample` reading sends
  it and `GET_MODULE_VOLTAGE` (eleven a reading): reads with no write, in every run since September (the handlers are in
  E118's change record, "PMIC voltage-register reads, no write"). Whether "no PMIC command" covers such reads is **an open
  question for the owner and Roman**, not a violation; the governor moves of 1 November (E77, E118, E120) used a build with
  both reads off, and the Q134 READMEs that used the stock build disclose its reads. `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS`
  is different: it writes the PMIC's firmware-management command register twice (E114's C1), a PMIC command by E85 C1's
  standard, and it was sent as a read-only identity read by E69 and E72 (27 Oct), E79, E82 and E84 (31 Oct), E114 (1 Nov),
  the version-3 check's nine passes (25–26 Sep, `tools/claims-v3/tel/block.sh`) and the aifoundry1 fix of 25 Sep; dated notes
  in E69's, E72's, E79's, E82's and E84's data READMEs say so. Take a card's identity by uptime continuity instead
  ([05-claims.md](05-claims.md), "Q134", the disclosures).
- **Dated note, Mon 2 Nov 2026 (Q136's records): the open question above is answered.** The owner's ruling of 2 November
  2026 allows read-only PMIC voltage-register reads ([AGENT.md](../../AGENT.md) §5, "Device commands"), so the stock
  `ettelem`'s `GET_ASIC_VOLTAGE` and `GET_MODULE_VOLTAGE` reads are allowed; every Q136 card run used them (E126 alone sent
  244,020). Q136(w)'s audit classified every command from the source of BL2 0.22.0 ([its
  README](../reports/data/2026-11-02-q136w-write-audit/README.md)) and adds: `DM_CMD_GET_FRU` writes three PMIC FRU
  registers before it reads (never sent); the statistics reset (`--reset-ms`, type 1 and control 2) is two PMIC writes,
  `0x47` (the reset) then `0x43` (the snapshot the SP's own DM task sends every pass), and it also re-arms the PVT high/low
  latches and switches the SP's statistics trace off; `dev_mngt_service -t SPST:enable` (type 1, control 1), which
  `tools/claims-v3/tel/block.sh` sends, is another form of the same command, not the ruled reset;
  `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` overwrites the governor's RAM temperature input with the same integer mean the
  governor's own update writes (benign, E126's verifier); and the stock `ettelem` cannot set the SP's log level back to its
  boot default, WARNING.
- **The hottest shire on aifoundry1's card 1 is a latch** (dated, Mon 2 Nov 2026; E131 C3). `max(temp_c.minshire)` there is
  the PVT's high-water latch, 65 °C in all 24,157 of E131's samples and since at least E112(b) (1 November), set before
  those sessions, while the shire mean peaked at 62 °C. Give the shire mean beside any "hottest shire" maximum on that card.
  The statistics reset is what re-arms the latch (Q136(w)).
  **Dated note, Tue 3 Nov 2026 (Q138's records; E145 C4): both outer entries of `temp_c.minshire` are latches, on every card
  read.** At `836a4ab` the firmware fills the low and high entries from the sensors' latched sample low and high (`smpl_hilo`),
  which the reading path (`pvt_get_ts_data`) never clears: they read 46 and 65 °C in all 26,916 of E145's samples on card 1, while
  only the mean moved (51–56 °C), and the high entry reads 87 °C in every sample of E138 on aifoundry3, where E144 found the 34
  high latches unchanged from 31 October through all its ticks. A die stop on "any minion-shire reading" is therefore at least a
  stop on the mean, and a stop on the hottest shire only if the latch updates on every conversion, which the source does not show;
  on aifoundry2 E146's die-stop test fired on the high entry's latched 69 °C at its first sample. The same latch is behind E128's
  C3 note ("65 °C in the hottest shire", for E108's session) and E137's and E128 C6's "no shire above 65 °C".
- **Card 1's minion rail sometimes reads its running maximum** (2 November 2026, E145). On aifoundry1's card 1 `sp.minion_w[0]`
  returned 34.50 W, the rail's running maximum, in 15 of E145's 26,469 block samples and 8 of 18,959 in E137's card-1 blocks, and
  in none of 31,491 on aifoundry3 (E130, E138); one such sample raises a run's rail window by about 1.0 W, and four of them in
  three B runs left E145's registered interval six times wider than planned (its C3). Why the reading returns that register is not
  established. Register a rail-spike filter on this card before the data; E137's post hoc rail figures on card 1 were read without
  one. Data: [`2026-11-02-e145-int8-b-card1`](../reports/data/2026-11-02-e145-int8-b-card1/README.md), `posthoc/rail-spikes.json`.
- **aifoundry3's minion rail stays clean** (3 November 2026, E151). E151's registered rail filter, which marks E145's 15 glitch
  samples on card 1 and nothing else, marked none of E151's 19,259 samples and none of 628,575 on aifoundry3 since 1 November.
  Data: [`2026-11-03-e151-int8-b-aifoundry3`](../reports/data/2026-11-03-e151-int8-b-aifoundry3/README.md), `rail-census.json`.
- **Card 1's build was not read on 3 November** (E157 C3). It is release 1.4.0 with BL2 0.22.0 as card 1 has reported since 31
  October (E82 A1); a same-day read would have taken the firmware-revisions query, which these rounds do not send. On card 1 the
  DDR die rail moves for E156's `el_64z`, where aifoundry3's stays still, and no telemetry field reads the PMIC's own temperature,
  so the margin to its 75 °C over-temperature alarm was not measured (E156 C6).
- **On aifoundry3 the `ettelem` that runs is not the reviewed build** (dated, Mon 2 Nov 2026; E132 C1, E134 C6). The
  `build/ettelem/ettelem` in its binaries tree (sha256 `16037641…`, built 25 September) comes from lab `de262730`'s
  `tools/ettelem/ettelem.cpp` (`ba9a0ac3…`), not the `a6cf931b…` Q136(w)'s table binds to that path; its `config()`,
  `sample()`, `Dm::get()` and `Dm::resetStats()` are byte-identical, so every class stands, and the table should gain that
  source as a reviewed variant. The card's own 0.22.0 is the non-public thermal build first flashed on 7 October, which
  answers command 74.
  **Dated note, Tue 3 Nov 2026 (Q138's records; E144 C5):** E144 classified command 74's group 0, the per-sensor reading its
  sampler sends at 10 Hz, READ from the held patch source, with a residual: the running build answers raw codes on group 0, which
  neither held form does, and is unhashed, while the card's 34 high latches read unchanged from 31 October through all of E144's
  ticks, so no latch reset ran. The shared `tools/claims-v3/dmcmd_table.json` still lists command 74 UNCLASSIFIED; E144's own
  table, `tools/claims-v3/e144/dmcmd_table_e144.json`, carries the class and the residual.
- **Throttle residency** (`DM_CMD_GET_MODULE_RESIDENCY_THROTTLE_STATES`) is a copy from the service processor's RAM and
  touches no PMIC; nothing clears it but a restart, the statistics reset included (Q134(a)). Its raw state numbers depend on
  the build: IDLE 0, UP 1, DOWN 2, SAFE 3 on BL2 0.22.0, and POWER_SAFE raw 5 on 0.18.0 and 0.20.0. A read of a state that is
  no state (raw 4–6 on 0.22.0) fails and logs two SP errors (E77's F1), and the lab's `ettelem-dv2` builds (`ettelem-hpl`,
  `ettelem-e77`) take raw states 2–6 only, refusing a call that names raw 1 before opening the device (E119's C3, E120's A1):
  ask for 2 and 3.

## The sensor reads whole degrees — use the step times

A run's temperature rise read straight off the sensor is only good to about half a degree, which is useless
for a 0.1 °C effect. The trick used throughout: **the times at which the reading steps from one degree to the
next are sharp**, so fit the one number (the heating power) that, put through the thermal network and rounded
the way the sensor rounds, reproduces that run's readings.

This recovers the rise to about 0.03 °C on repeated runs, and the recovered heating power agrees with the
electrical measurement to about 1 W. It cannot resolve workloads that never move the reading — for the three
coolest patterns it only bounds the rise below about half a degree.

Power needs none of this. It reads in 10 mW steps.

**A finer reading exists on aifoundry3's firmware build (E89, 31 October 2026).** Command 74
(`DM_CMD_GET_ASIC_PVT_SAMPLES`), group 0, returns each of the 34 minion-shire sensors' **raw 12-bit code**, 0.061 °C a
code, converted with the firmware's own formula (one set of constants for every sensor, no per-sensor calibration). The
firmware's integer mean rebuilt from the codes equals the reported die reading in 98.1% of 22,976 samples, so they are
the governor's sensors; that reading runs about 1 °C below the codes' mean, because the firmware truncates twice (each
sensor to a whole degree, then the mean). At idle each sensor's code has an SD of about half a code, and the 34-sensor
mean moves in 0.0018 °C steps with 0.005–0.008 °C of noise a sample — enough to resolve heat on int8 kinds that the
whole-degree reading cannot. 🛑 Two traps. The command exists only on the thermal firmware build flashed on 7 October,
and its group 0 returned whole degrees then and raw codes on 31 October, with the card reporting release 1.4.0 / BL2
0.22.0 (E79): probe what a card returns, read-only, before a run relies on it. And **group 6 resets the sensors'
latches — a write: never send it** (`tools/claims-v3/e89/pvt_sample.py` refuses every group but 0 and 4). Data:
`docs/reports/data/2026-10-31-e89-heat-low-power/README.md`, result 3 and "Joins and traps". **Read again on 1 November
2026 (E97):** still raw codes (1,960–2,004 at a 53 °C reading, read-only probe first), all 150,295 samples carry 34 sensors,
the rebuilt mean equals the firmware's in 98.3%, no fault bit, and the high latch never moved backwards. "A read" rests on
behaviour: the handler's source is not in the firmware copy we hold. The command was never sent to aifoundry2 (E98). And no
kind is read per sensor by this: every launch runs on all 32 shires.

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

**Since the October cooling changes the cards no longer reach 80 °C this way (E60, 20 October 2026).** Twenty 2 s
random-fp32 heater launches took aifoundry2 and aifoundry3 from about 50 °C to 64 °C and aifoundry1's card 0 to 60 °C
(`docs/reports/data/2026-10-20-bitflip-ladder/*/hl-probe/p1`). E60 therefore launched at a 58 °C reading (57 °C on
aifoundry1's card 0) with a 1 °C pre-heat: approaches took 1–10 s, a 4 s run about 10 s of wall clock. Below 65 °C
the governor-free cards (aifoundry2, aifoundry1's card 0) run a busy launch at **800 MHz** (0.618 and 0.604 V),
stepping 600 → 700 → 800 MHz within 0.3–1.4 s of the launch, so a measurement window must start after the step
(E60's amendment A2); only aifoundry3, pinned, measures 600 MHz there. Leakage at 58 °C is 0.2–0.4 W per °C.

## The lab machines and their four cards are not interchangeable

Updated 2026-09-25: aifoundry1's two cards answer since 15:02 that day, so there are four cards on three firmware
releases; three are usable for measurement, since aifoundry1's card 0 overheats and takes nothing sustained (amendment
A4). Updated 2026-10-02: card 0 is usable again (its fan was replaced) and aifoundry2's card was out of service (its
cooling failed) until 2026-10-06, when its fans were set to full speed: all four cards were in service again. Updated
2026-10-07: aifoundry2's card was out of service again from 16:46 that day. Updated 2026-10-09: a two-fan 92 mm
bracket was fitted at that card and it is back in service, so all four cards are in service again (below). Before
using a card for anything comparative, read its governor configuration. Two read-only commands:

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
| Firmware release (BL / PMIC / minion) | **1.4.0 (BL1/BL2 0.22.0 / PMIC 1.5.0 / minions 0.25.1)**, read fresh 27 Oct 2026 under E69's G0 gate; 1.3.1 (0.20.0 / 1.5.0 / 0.23.0) in every earlier record here, and the `0.20.0` in `et-lab-manifest` is the **host driver's** version, not the card's | **1.4.0 (BL1/BL2 0.22.0 / PMIC 1.5.0 / minions 0.25.1)**, read 31 Oct 2026 (E79); 1.3.1 (0.20.0 / 1.5.0 / 0.23.0) in every earlier record here | **1.4.0 (BL1/BL2 0.22.0 / PMIC 1.6.1 / minions 0.25.1)**, read 31 Oct 2026 (E84 A1); 1.4.1 (0.21.2 / 1.6.1 / 0.24.0) as recorded on 25 Sep | **1.4.0 (BL1/BL2 0.22.0 / PMIC 1.3.0 / minions 0.25.1)**, read 31 Oct 2026 (E82 A1); 1.2.0 (0.18.0 / 1.3.0 / 0.22.0) as recorded until then (START.md has carried release 1.4.0 since 7 Oct, `1c00d6ff`) |
| TDP the driver reports | 65 W | 65 W | 65 W | 65 W |
| **TDP the firmware uses** | **65 W** | **0 W**, set at every boot (below) | 65 W | 65 W |
| Clock | firmware DVFS: 600, 700 or 800 MHz; above 600 only below about 68 °C. In this chassis the die never read below 65 °C in the version-3 campaign (336,070 samples, 25–26 Sep), and over DV2's 20 h validation (28–29 Sep) it idled at 71–76 °C in 327 of 378 cycles, so it runs at 600 MHz unless it starts cold | **600 MHz** (NoC 400), never seen higher (10 Hz telemetry), pinned by the zero TDP: no governor line in its trace since 25 Sep (E41 TEL-G), and its throttle residencies all 0 after 2 d 8 h up (28 Sep; E51, development); it makes no thermal step at any temperature. That was read as 0.20.0's latch; at the BL2 0.22.0 it reports (E79) the zero TDP is a reversible pin ("The governor's two knobs"; Q130(d)) | firmware DVFS under BL2 0.22.0 (TDP 65 W / 65 °C); idled at **600 MHz / 519 mV** on 31 Oct (E84), where it idled at 300 MHz (`low_power`) on 25 Sep under 1.4.1; the governor acts only while a kernel runs. 🛑 **fp32 random data at 800 MHz trips its PMIC's 75 W over-power alarm**: a 300 MHz safe state about every 1.1 s (E84; "aifoundry1 card 0's PMIC over-power alarm", above) | **600 MHz in all 318,667 samples of the three-card check (25–26 Sep)**, and in the SP's own minimum and maximum, although 9,461 were busy at 45–65 W at 64 °C or less and the mean reached 88 °C: its governor does not raise the clock (active power management off, or latched; asked the lab). Its build was recorded as stepping 50 MHz between 300 and 700 MHz (BL2 0.18.0), so it could never reach 800; under the BL2 0.22.0 it reports since 31 Oct it still reads 600 MHz in every sample (E82, E88, E91) |
| Idle | **51 °C and 23.2 W since 9 Oct** (a two-fan 92 mm bracket at the card); about 64 °C and 27 W from 6 Oct until 03:55 on 7 Oct, when the cooling at the card got worse, and out of service from 16:46 on 7 Oct to 9 Oct; before 6 Oct 31–36 W at 73–80 °C (27 W cold); on the night of 28–29 Sep (DV2's idle watch) 73–75 °C and 31.4–32.5 W at 20:45–21:09 and 00:11–01:00 PDT, 59 °C and 25.4–25.6 W at 22:12 and 23:15–23:18 (idle cycles only; its heating sessions ran 22:13–23:56); over the whole watch, to 16:48 on 29 Sep, 59–76 °C, 71–76 °C in 327 of 378 cycles, and never below 65 °C after 23:18 | 23.6 W at 50 °C (25.1 W at 56 °C under the runs); the die idles at 55–57 °C since the host changes of 25 Sep | 18.6–18.8 W at 300 MHz; 26 W at 600 MHz; 49 °C (hottest sensor 53 °C) and 19.6 W after its fan was replaced (2 Oct); 19.0–21.2 W at 600 MHz between E84's runs (31 Oct) | 33–35 W at 600 MHz and 57–62 °C; 33.0 W (E91, 31 Oct) |
| Use it for | **anything since 9 Oct 2026**, with the two-fan bracket at the card (below), keeping a temperature stop on long full-load runs; out of service 7–9 Oct and 2–6 Oct; in service 6–7 Oct with its fans at full speed; before that the main card | compare switching power over idle, never absolute watts | anything since its fan was replaced on 2 Oct 2026 (52–53 °C under sgemm bursts), but **not fp32 random data at 800 MHz without a stop for its PMIC alarm** (E84; Q130's evening round left the card out for it); from 25 Sep until then **nothing sustained: it overheated** (below) | anything; it peaked near 71 °C under the campaign's smoke blocks. Filter its board readings for launch-gap dips (the telemetry table) |
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
all: under its own 0.20.0 build the zero TDP leaves the power task in a loop that cannot exit (🛑 **a 0.20.0 reading; BL2 0.22.0 has no such loop, and there a TDP of 0 is released by writing the TDP back — E72, below**), and the first mean
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

**aifoundry1's card 0 overheated, from 25 September until its fan was replaced on 2 October.** On 25 September about
ten minutes of short smoke blocks took its die to 98–102 °C. Right after them it read 115–117 °C with nothing running
and drew 66–71 W at 600 MHz (leakage at that temperature), until its firmware dropped it to 300 MHz and it cooled from
104 to 78 °C in eight minutes. Card 1 beside it peaked at about 71 °C under the same smokes. It was a cooling fault
(fan, heat sink or airflow) that the 300 MHz low-power idle hid. Until 2 October no sustained work ran on it; the
machine's login banner said so, and the campaign excluded it (A4). **Its fan was found broken and replaced on site on
2 October** (host up 12:59). After the repair it idled at 49 °C (hottest sensor 53 °C, 19.6 W) against 65 °C with a
123 °C hot spot before, and 8 minutes of sgemm bursts (8 s of `-n 1024` under the lock, then 2.5 s free, 44 bursts)
held it at 52–53 °C, hottest 56 °C; card 1 beside it, the same test just before, settled at 59–60 °C, hottest 63 °C.
Readings are the live collector's, taken in the gaps (`docs/reports/data/2026-10-02-fan-fix-aifoundry1/`). The owner
put it back in service that afternoon, at about 13:30 (the new-user brief `docs/lab-start/START.md` since its sixth
edition, `d124ef0`): select it with `ET_DEVICES=0` and `/run/lock/etsoc-shire0.lock`. The same card's PCIe link also
logs about one corrected receive error per second at its root port, at a rate that changes from boot to boot. It does
not stop the card, but link replays can add DMA latency. A reseat is pending. Since 25 September the kernel log for
that link is rate-limited, and the error counters still count.

**Selecting one card on a two-card host.** With aifoundry1's device layer, `ET_DEVICES=<n>` makes a program open only
card n, which it then sees as device 0; programs built on aifoundry1 against its `/opt/et` honour it, `ettelem`
included. `tools/claims-v3/lib.sh` sets it from `V3_DEVICE=<n>`. `/opt/et/bin/dev_mngt_service` (and
`et-powertop`) is the stock build: it ignores `ET_DEVICES` and opens every card's management node even with
`-n <N>`, so run it only when both cards are free (`et-who`). On 26 September our stock `dev_mngt_service` call for card 1 collided with a
watcher holding card 0: 13 refused opens in the kernel log and 10 aborts with core dumps. Since 2 October two people
may work on aifoundry1 at once, one per card. `et-who --check` there counts both cards (exit 1 if anyone holds
either), so a script for one card looks for its own card's holder lines (those starting `/dev/et<N>_` or
`lock:etsoc-shire<N>.lock`) and stops on exit 2.

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

**Updated 2026-10-14.** The kernel row above is long out of date, but nothing here dates when each host moved.
`uname -r` on 14 October: aifoundry2 runs **7.0.0-38** (since its 9 October restart), aifoundry1 and aifoundry3 run
**7.0.0-34**, both with 7.0.0-38 installed and a restart still pending (`/boot` holds both kernels on all three;
`/var/run/reboot-required.pkgs` names `linux-image-7.0.0-38-generic` on those two and is absent on aifoundry2);
aifoundry3's waits for the lab user working there. aifoundry3 was **already on 7.0.0-34 on 29 September**, before the
30 September power cycle, by its own manifests in `docs/reports/data/2026-09-29-nocr/raw/aifoundry3/`, while the same
campaign recorded 7.0.0-31 on aifoundry1 card 1 and aifoundry2. So do not date a host-side baseline's kernel from a
calendar date: take it from the run's own `et-lab-manifest` line, which every run here records. And aifoundry2's host
side is no longer comparable with the other two's: say which kernel a run used.

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

## aifoundry2's card dropped off the bus while idle (1 October, 09:42 PDT), and is out of service (2 October)

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
follow the CPU temperature (no fan speeds are visible from Linux). Fix on site: the BIOS fan settings (the lab report said Smart Fan 5; on this BIOS it is Smart Fan 6:
Fan Stop off, a floor of at least 50%), copied from aifoundry3 (lab report SH5); done on 6 October with every fan at
full speed (below). Until then, a host that sits idle
lets this card overheat, and no firmware cut-off stops it.

**Out of service since 2 October.** After the full reset at 10:53 no process held the idle card, and the host CPU
read 37–52 °C (mostly 37–46 °C). The card heated from 45 °C and 21.9 W to 95 °C and 48 W in 56 minutes, then ran away: a 138 °C
mean (hottest sensor 144 °C) and 134 W at 12:02:01, and it was off the bus at the next read. No firmware cut-off
acted. The same had happened at 07:42, 57 minutes after the 06:45 full reset (126 °C, 103 W). A fit puts the tipping
point near 97 °C: 13.6 W plus a leakage part doubling every 23 °C, against cooling through about 0.9 °C/W into air at
about 51 °C, where aifoundry3's identical card sees about 31 °C
([`docs/reports/data/2026-10-02-idle-runaway-aifoundry2/`](../reports/data/2026-10-02-idle-runaway-aifoundry2/README.md),
`fit.py`, `fit.txt`). So the fault is the air reaching this card, not the chip. Nobody runs anything on this card until
the lab fixes that air (lab report SH5). A full reset brings it back, but it then looks healthy for about an hour
while it heats: that hour is not a sign that it is fixed. The machine aifoundry2 itself stays up, with the git
checkout; only its card is out.

## aifoundry2's card back in service: every fan at full speed (6 October 2026)

**It held for about a day: out of service again since 7 October, 16:46 PDT (the next section).**

On 6 October (15:54–16:07 PDT, on site) every fan header in aifoundry2's BIOS (Gigabyte Z590 AORUS MASTER; Smart Fan 6,
F6) was moved from the Normal curve, which follows the CPU temperature, to Full Speed (CPU_FAN set, then TUNE ALL; Fan
Stop stays Disabled, control mode Auto), and the card was brought back with the full reset. On the BIOS screen every fan
followed the CPU at 43 °C while the card's slot sensor (PCIEX16) read 57 °C; five minutes after the change it read 55 °C.
Measured since (`docs/reports/data/2026-10-06-fan-fix-aifoundry2/`, [the 6 October page](https://spacesheep.dev/@yaroslavvb/aifoundry-lab-6-october)):

- **Idle:** about 64 °C and 27.4 W, steady (16:16–16:22). Five minutes after coming back on the bus, the 2 October run
  and this one both read 64–65 °C at about 28 W, but on 2 October the card was heating by about 2 °C a minute there, and
  this time it cooled. By the 2 October fit, the cooling now carries the card's 27 W at 64 °C where it carried about
  14 W, as if the air reaching the card were about 39 °C instead of 51 °C; that moves the idle tipping point from about
  97 °C to about 122 °C.
- **The 8-minute sgemm burst test** (aifoundry1's of 2 October, stops at an 85 °C mean or 95 °C hottest): 44 bursts,
  all exit 0; 66 to 76 °C at 33 W, still rising about 1 °C every two minutes at the end. aifoundry1's cards ran it at
  53–54 °C (card 0) and 59–61 °C (card 1).
- **The 21 September long session's heavy run** (`run_horace_long.sh`, `randn 32 600 1`: heat to 84 °C, idle to
  80 °C, then random data on every minion, stop at 90 °C): 37.3 s to the cap at about 71 W, against 19.3–26.5 s on
  21 September (runs 1, 4, 8 and 23); 75 °C three and a half minutes later, where on 21 September the card settled at
  81–82 °C. The fans slow the spike but don't remove it: full load on every minion still needs the cap or short runs.
- **A trap in reading it:** the `max` of the live collector and of `ettelem` (`minshire[2]`) is the highest reading since
  the card's statistics were last reset (`since_reset_ms` −1: never, so since boot), not the hottest sensor now. After
  the heavy run it read 93 °C while the mean cooled from 75 °C; on 2 October it tracked the mean only because the card
  heated the whole time.

The setting lives in the BIOS: a BIOS update or a CMOS reset puts the Normal curves back.

## aifoundry2's card ran away again at idle (7 October 2026), and is out of service

**Back in service since 9 October 2026, with a two-fan bracket at the card (the next section).**

**Out of service since Wed 7 October 2026, 16:46 PDT.** A day after the fan fix the idle card ran away and dropped off
the PCIe bus exactly as on 2 October. The cause is the cooling at the card, not the card. From the live collector's
records (`docs/reports/data/2026-10-07-idle-runaway-aifoundry2/`, `analyze.py`; the page
[aifoundry2-idle-runaway-7-october](https://spacesheep.dev/@yaroslavvb/aifoundry2-idle-runaway-7-october)):

- **Back on the bus** at 16:05:32 on 6 October. The fix's load tests held it at 16:22:30–16:35:05, and nobody held it
  after that. From 17:00 to 03:50 it idled at 63–70 °C and 26.9–30.3 W.
- **03:55 on 7 October: the cooling at the card got worse, in one step.** It went from 64 °C (27.6 W) to 78 °C (34.5 W)
  by 04:50, then held 74–78 °C through the morning. The host was idle (0.5% CPU), and its own sensors did not move:
  NVMe 45.9 → 46.3 °C, network chip 54.1 → 53.8 °C, CPU 39 → 38 °C (the 50 minutes either side).
- **At about 14:25 it got worse again:** 85 °C at 14:44:50, 90 °C at 15:30:25 (43.3 W), 100 °C at 16:39:55. The last
  reading was at 16:46:40: a 138 °C mean, hottest sensor 144 °C, 133.45 W. There was none after 16:46:45. On 2 October
  the last reading was 138 °C, 144 °C and 133.65 W.
- **The card itself did not change.** At every temperature its power matched the 2 October leakage law,
  13.56 + 2.025·e^(0.0300·T) W: 0.25 W rms over 17,678 readings, and within 0.44 W at every whole degree it held
  for a minute or more. Work, or a change of clock or voltage, would have left that curve.
- **What the cooling did.** By the 2 October heat balance (R 0.897 °C/W, C 296 J/°C; air = T − R·(P − C·dT/dt)), the air
  temperature the card's heat balance needs was 39.4 °C in the night, 45.6 °C after 03:55 and 50.7 °C after 14:25. An
  idle card has no steady temperature above 51.5 °C (the tangent at 97 °C). The model's steady temperatures for
  39, 46 and 51 °C air (63, 76 and 91 °C) are what the card did. These are model numbers: a loss of airflow shows up
  as warmer air.
- **The kernel** logged 5 corrected receiver errors on the link at 16:46:32–36. At 16:55:02 the driver's queue sync
  read the card as all ones (`head_remote: -1`). At 17:01:20 root port 00:01.1 was reset; what triggered it is not
  known. The card did not come back: it is not in `lspci` and has no `/dev/et0` nodes (`kernel.txt` there).
- **The fan is not known.** No fan sensor driver is loaded on aifoundry2, and loading one needs root. Two other causes
  are ruled out. The BIOS setting stands, because there was no reboot since the fix. Linux never switched a fan: the
  ACPI fans' `stats/total_trans` is 0 since boot. A fan near the card that stopped, slowed or moved, or something
  blocking its air, fits a step at 03:55 that nothing else felt. Look on site, and in the BIOS's Smart Fan 6 page,
  which shows each header's RPM (System 5 read 2,368 RPM at full speed on 6 October).
- **Nothing on the card stopped it,** from 65 to 138 °C: its firmware's thermal loop runs at idle but cannot go below
  the 600 MHz the card idles at, and the safe state is a no-op ("Nothing limits the die's temperature", above).

**To bring it back:** fix the cooling at the card on site, then do the full reset as root (the cold reboot from
2 October, above); a warm reboot or a slot reset leaves it off the bus. Then watch it: after a reset it looks healthy for
about an hour while it heats, and this time the trouble began 12 hours in. Brought back on 8 October at 14:47, the idle
card crept up from about 71 °C and ran away again at 19:36–19:49 (a 138 °C mean, 134 W) and stopped answering. The fan
under the card was found stalling and replaced on 9 October (the next section).

## aifoundry2's card back in service: a two-fan bracket at the card (9 October 2026)

On Friday 9 October (14:55–about 15:17 PDT, on site) the 120 mm fan clipped under aifoundry2's card, which had been
stalling since 7 October, was taken out, and a two-fan 92 mm PCI-slot bracket was fitted in the slot beside the card:
one Pano-mounts fan (3,000 RPM, 3-pin) and a Cooler Master SickleFlow 92 (650–2,300 RPM, 4-pin), which replaced the
bracket's second fan because its cable was longer. The card is passive, and the bracket blows straight across its
heatsink. The host was booted at 15:07, before the bracket was back in, and in those nine minutes the idle card heated
by about **4.4 °C a minute**, from 44 to 87 °C (21.6 to 40.8 W): **never power this card without the bracket.** With the
fans on it fell to 51 °C by 15:24.

Measured that afternoon with the 6 October scripts, unchanged but for their folders
(`docs/reports/data/2026-10-09-fan-swap-aifoundry2/`, [the 9 October page](https://spacesheep.dev/@yaroslavvb/aifoundry-lab-9-october)):

- **Idle** (15:24–15:36, nobody holding the card): 51 °C and 23.2 W, against aifoundry3's twin card at 53 °C and 24.3 W
  in the same minutes. On the afternoon of 8 October this card idled at 71 °C and 30.8 W.
- **The 8-minute sgemm burst test** (15:36:44–15:44:50): 44 bursts, every one exit 0; the die went from 49 to 63 °C and
  **levelled off at 62–63 °C**. On 6 October the same test went from 66 to 76 °C and was still climbing at the end.
- **The heavy run** (`randn 32 600 1`, the 21 September protocol, 32 minions per shire): it ran its **full 600 s** with
  no stop and settled at **75 °C and 59 W**; three minutes after it the die read 54 °C. On 6 October the same run reached
  the 90 °C cap after 37 s, and on 21 September after 19–27 s. All 1,584 launch records report `ok`, and neither the
  driver nor the root port counted an error.
- **The card itself is unchanged:** firmware 1.3.1, the firmware's DVFS at 600 MHz in about 99% of samples with brief
  steps to 700–800 MHz, and no driver or PCIe errors anywhere in the afternoon.
- **The margin** (a one-node steady state with the 7 October leakage law, P = 14.39 + 1.836·e^(0.0308·T) W; model
  values): the cooling is 0.68 °C/W from die to air, the slope between the idle and full-load plateaus. The idle card
  has no resting temperature at all from 1.26 °C/W — 1.9 times worse cooling than today's — and under sustained full
  load from 0.81 °C/W, 1.2 times worse; the afternoon of 8 October works out to 1.18 °C/W. So the card is in service,
  but **long full-load runs keep a temperature stop** (85–90 °C), as the lab's scripts already do: 1.2 times is not
  much margin, and nothing on the card stops a runaway ("Nothing limits the die's temperature", above).

## The lab dashboard's maintenance sweep (11 October 2026)

On Sunday 11 October (16:40–23:00 PDT) the dashboard's four warnings were cleared
([the 11 October page](https://spacesheep.dev/@yaroslavvb/aifoundry-lab-11-october)). What it showed about the hosts:

- **The wired ports now have fixed addresses on all three** (Requests for Roman U29: aifoundry1 and aifoundry2 on 11 October,
  aifoundry3 on 13 October at 08:07). Since the 7 October cabling they had none, so NetworkManager retried DHCP every few minutes (about 30,000
  log lines a boot), its start-up never completed within `NetworkManager-wait-online`'s 60 s, and that unit failed at every
  boot, leaving systemd "degraded". The retrying profile was NetworkManager's unsaved default; `nmcli con mod` saved it into
  `/etc/netplan` (`90-NM-<uuid>.yaml`) with no default route, Wi-Fi untouched. The two reach each other over the cable in
  under a millisecond. No machine has rebooted with it yet.
  **Updated 2026-10-14.** The cable dropped earlier today and came back at 13:56 PDT on all three machines, at 1 Gb/s
  and full duplex, with about 0.5 ms between machines and the saved settings intact (`ip link` and `ethtool` both report
  the link up; each host's driver logs `link change old 0 new 1000` within seven seconds of the others). It is not yet
  dependable, though: every port has now lost carrier twice since these hosts booted (`carrier_down_count` reads 2,
  `carrier_up_count` 3). So read `cat /sys/class/net/enp7s0/carrier` and check it is 1 before measuring over the cable,
  and record which link a run used — the machines fall back to Wi-Fi while the carrier is gone.
- **Tailscale SSH with a command and a terminal leaves the pty owned by root**, with only the user's own processes on it (no
  `login(1)`, no utmp line), and can leave an empty root-owned pty behind. The dashboard read those as root logins; since
  `95c0fef` a root-owned pty counts only with a root process on it.
- **aifoundry1's root pool held 42 bad blocks in four files**, found by the 13 September and 11 October scrubs (none on
  9 August); the disk reports no media errors, and every restart in the log since September was a crash. A corrupt stage-1
  compiler build file was deleted, two llama.cpp vocabulary fixtures were restored byte for byte from their own git history,
  and the pool was cleared and re-scrubbed. One block is left, in a dangling git object of a departed user's clone.
- **The live monitor's 4 October fix (`efa3e8c`) runs on all three**: aifoundry2 since 11 October, aifoundry1 since
  12 October 08:01, aifoundry3 since 13 October 08:07. aifoundry3's kernel update still waits for its user's session to end. Its reader crashes about once in 24,000 runs, on exit, inside the vendor's management library
  (a receiver thread that is never joined), after the reading is printed.
- **The dashboard's half-hourly card sample has not run since 2 October.** aifoundry1 waits for a person to confirm card
  numbering for its 7 October boot; aifoundry2's quiet gate counts the management queue, which the 1 Hz monitor uses twice a
  second; on aifoundry3 a user was active. The page's temperatures come from the live monitor.
- **The kernel ring buffer holds about 50 minutes on all three**: AppArmor audit lines for `bwrap`, about 23 a minute, fill
  it, so `et-lab-health`'s per-card kernel-log counts cover the last hour; the journal holds the whole boot.

## aifoundry1 card 0's link is a lottery at each boot, and the hosts now retry it themselves (26 October 2026)

The lab lost power on Sunday 25 October at about 17:20 PDT. When it came back on Monday 26 October, all three hosts booted
by themselves within 28 s of each other, aifoundry2 first at 11:54:22. That boot gave aifoundry1's card 0 (root port
`00:01.0`, the top x16 slot) a bad link, and a cold reboot gave it another bad one:

| Boot | Card 0's link | Corrected errors at root port `00:01.0` |
|---|---|---|
| Sat 3 Oct 08:17 | 16 GT/s x8 | 697 in 4.5 days |
| Wed 7 Oct 18:17 and 21:28 (the lab's power) | 16 GT/s x8 | 26 in 3 h; 67 in 18 days |
| Mon 26 Oct 11:54 (power back) | 16 GT/s x8 | 34,552 in 3 h 6 min, about 3 a second, all receiver errors (`RxErr`), none at the card |
| Mon 26 Oct 15:02 (cold reboot, mode cold, type pci) | **8 GT/s x8, "downgraded"**: the 16 GT/s equalization did not complete | 0 |

Card 1 beside it, and aifoundry2's and aifoundry3's cards, trained at 16 GT/s with no errors at every boot. So the top
slot or card 0's edge connector is marginal at 16 GT/s, and the clean training after the 30 September power cycle was
luck, not a fix. A link this marginal is redrawn at every boot: the one at 15:02 is stable but at half the host
bandwidth (`63.008 Gb/s available PCIe bandwidth, limited by 8.0 GT/s PCIe x8 link at 0000:00:01.0`).

**Since 26 October the hosts redraw it themselves.** `et-boot-check` (in `tools/lab/host-recovery/`) checks every card
3 minutes after each boot: present, its driver started, its link at the speed its root port targets, and at most 30
corrected errors at the root port in 60 s. When one fails, it does the cold reboot itself, at most twice in 24 hours and
only within the first 20 minutes after boot, with no card held, no CI job running and nobody at a terminal; otherwise
the unit fails and shows as a failed unit in `systemctl --failed`, `et-lab-health` and the dashboard.
`et-boot-check --status` shows its runs.

Three host facts from the same afternoon, each read on all three hosts:

- **They power on by themselves when power returns.** The chipset's `AFTERG3_EN` bit (`GEN_PMCON_A`, at `PWRMBASE`
  0xFE000000 + 0x1020) reads 0 on all three, which agrees with the unattended boots at 11:54. aifoundry2's BIOS power
  setting (AC BACK) is therefore no longer "Always Off", as earlier notes said.
- **The chipset watchdog cannot reset them.** The BIOS (Gigabyte Z590 AORUS MASTER, F5 on aifoundry1 and aifoundry2,
  F6 on aifoundry3) routes the TCO timeout to its own SMI handler and locks it (`TCO_LOCK` and `TCO_EN` set): armed for
  10 s and left to expire on aifoundry3, it did not reset the machine. So a hung host, like aifoundry1 on 30 September,
  still needs a power cycle from outside. `kernel.panic` is now 10 on all three, so a panic at least reboots.
- **After the power came back, aifoundry1 and aifoundry2 booted with the ACPI interrupt switched off.** The kernel logged
  `irq 9: nobody cared` and disabled IRQ 9 after 100,001 unhandled interrupts at boot. That happened at aifoundry1's
  boots after the lab's power events of 7 October and 26 October, and at aifoundry2's on 26 October (its journal starts on
  10 October). aifoundry3 never did, and no host did at the cold reboots of 26 October. In such a boot the OS never sees a
  short press of the power button, so shut down from a shell, or hold the button for a forced off.

**Dated note, Mon 2 Nov 2026 (Q136(w)):** both automatic reboot paths still stand on all three hosts, beside the owner's rule of
2 November 2026 of no power cycles and nothing that risks one: `et-boot-check`'s cold reboot after a boot whose card link
trained badly, and `kernel.panic = 10`, a reboot 10 s after any kernel panic, which a driver fault during a run could set off
(`tools/lab/host-recovery/lab-panic.conf`). Neither was changed; they are named here for the owner's awareness
([the audit](../reports/data/2026-11-02-q136w-write-audit/README.md)).

## aifoundry3's working temperature under the hl heater, and the gate that rules out its own protocol (26 October 2026, E65)

E65 ran 123 approach launches and 48 no-approach launches on aifoundry3's card at the latched 600 MHz, 521.7 mV,
through E60's `hl/block.sh` heater. Two things about this card and this protocol came out of it. Data:
`docs/reports/data/2026-10-26-e65-bit-prices-hart-ladder/` (`logs/queue-ab.log`, `logs/queue-d-a7.log`,
`runs-blockD.csv`, `reduce-blockD.txt`).

- **The approach tops out at 59–61 °C, not E60's probed 64 °C.** Every approach in E65's blocks A and B peaked at
  **59.0 °C ×3, 60.0 °C ×107, 61.0 °C ×13** before idling back to the 58 °C launch — 107 of 123 at exactly 60.0.
  E60's heat probe had put this card's plateau at 64 °C under 2 s heater bursts, and E65's block D was registered
  for a 65 °C launch on the strength of it. It was never reached, and the block had to be rewritten mid-run
  (amendment A7). **Plan a block on this card for a 60–61 °C ceiling under the `hl` duty cycle**, and treat E60's
  64 °C as an upper bound from a different burst pattern, not as a usable setpoint. Whether an approach can *hold*
  63–65 °C here is still untested: A7 inferred it could not and switched to no approach at all, so no 63–65 °C
  setpoint attempt exists.
- **A run-to-run climb is available for free, and the standard drift gate throws it away.** With no approach between
  runs (`--preheat 0`), the card warms monotonically: E65's eight A7 passes launched across **55–62 °C** (55 ×2,
  56 ×1, 57 ×5, 58 ×4, 59 ×8, 60 ×13, 61 ×12, 62 ×3; median 60), about 2 °C within each pass and 7 °C from the first
  pass to the eighth. That is more temperature leverage than any approach regime on this card can buy. **But all
  eight passes were then rejected by the standard pass-level gate** — `anchor_pi` must not drift more than 0.3 W from
  a pass's first run to its last — with drifts of **+0.57 to +0.74 W**, every one the same sign, at a measured leakage
  slope of 0.069 W/°C. The climb that makes the spread is the climb that trips the gate, so **a no-approach regime is
  rejected by that gate by construction, 8 of 8**, and the regime measures nothing.

  **The rule this implies:** a no-approach regime must have its drift gate restated *before the data* as a rate —
  watts per degree of the pass's own climb, tested against the leakage slope — or be replaced by a within-pass
  control. A gate written for an approach regime silently voids a protocol that removes the approach. E65's
  amendment A8 caught the sibling problem (the launch-*reading* gate also assumes a setpoint) and missed this one;
  the usable block-D data came only from A9's gated 61 °C setpoint regime, which reached 61.0 °C with zero skipped
  runs in 36 and passed the gate on five of its six passes.

## Traps that cost time here

- **A kernel's issue rate is set by where its loop sits, not by its data (E61, 21 October 2026).** In enercat's
  vector modes every loop body is 64 or 128 vector ops plus eight scalar instructions, and the measured rate falls into two
  levels, 0.6088 and 0.5814 ops per cycle per hart, according to the loop head's address mod 32 (6 or 22): 14 of 14 modes,
  all three cards, constant in the data to 1e-4. The vector unit itself retires one op per cycle per hart; the rest is the
  loop's own overhead. Rebuilding the kernel moved mode 179 (`fxor.pi`) from 0.5791 (E60's build) to 0.6088, so compare
  watts only between runs of one build and one mode, and per-op energies against each run's own op count
  (`tools/claims-v3/dtf/README.md` amendment A2; `docs/reports/data/2026-10-21-dtf/proof/enercat-df-aifoundry2.dis.txt`).
- **aifoundry2's kernel ring buffer keeps only about an hour (7 October 2026).** AppArmor audit lines from `bwrap`
  arrive every 15 s, and they had pushed the card's 16:46 PCIe errors out of `dmesg` by 17:40. `journalctl -k` needs the
  adm or systemd-journal group. Copy a card's kernel lines into the data folder as soon as it misbehaves.
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
  unchanged workload. Record enough telemetry to notice. **Host compute on any box beside a settled reading (1 November
  2026):** E97's plateau on aifoundry3 moved +0.796 °C within a minute of a CPU burst on aifoundry1, this same run's own
  desk compute, 6 of 16 threads for about 2 min 15 s. That does not show the burst moved the die: two more moves have no
  burst, a chance match is roughly 1 in 10, and the idle did not follow other lanes' card sessions, which carry more heat.
  It is all the evidence the record holds for the rule, which stands: no host compute on any box beside a card run, and read
  an inlet beside a settled reading. **A login stops a queue:** the runners' other-user check ended E98's P2 mid-run on
  another lab user's login, so register a spare probe. (Dated note, 1 Nov 2026: by the owner's ruling of 1 November 2026 another lab user's **idle** login no longer
  blocks a run on aifoundry2, as on aifoundry3; a fresh login or any activity still stops it, as one ended E111's W1
  at 14:36:12.) Other users are part of the environment too
  (2026-09-25): CI runners on aifoundry1 and aifoundry2 can take a card at any time, and a demo service on aifoundry3
  can launch on its card without taking the card lock. Check `et-who` before and after a run. The hosts reach the
  network over Wi-Fi only and roam between access points: aifoundry2 lost its Tailscale connection for 12 minutes on
  23 September. Start long runs detached (`setsid`, [getting-started.md](../getting-started.md) §7).
- **aifoundry3 can be heated.** Earlier sessions never took it past about 61–66 °C, but those were short bursts:
  150 back-to-back 2 s random fp32 matmul launches took its die from 55 to 88 °C (V3-IDLE, pass 1, 2026-09-25).
  Its heat sink is faster than aifoundry2's, not unbounded.
- **A session's automatic leakage slope wanders, so register one** (1 November 2026). E91's 0.422 W/°C on aifoundry1's
  card 1, against 0.20–0.24 elsewhere, is still unexplained; E93, E94, E103 and E104 froze E82's 0.2414 W/°C, and the
  automatic slope read 0.2959 on E95, 0.3298 on E101's first session and 0.0046 on E99 on aifoundry3.
  **Dated note, Sun 1 Nov 2026 (Q133, E112):** card 1's automatic slope with the dips removed read 0.414 and 0.417 W/°C in
  E112's two halves (E91 0.422), against E82's 0.241 with dips kept. It moves absolute D by about 0.5 W in fp32, makes
  about half of the card scale's gap (1.054 at each session's own slope, 1.028 at one slope on both) and decides E91's
  R5, and it does not move ratios to random. E112 registered `auto` without citing this bullet ((a) by re-running E91
  unchanged, (b) to pair with E95's dips-removed arm); read at E82's 0.2414, R5 would pass and (b) would stay NOT SCORED.
  The zeros-line gate set E112's third (b) pass aside by 0.003 W, as it had set E91's first pass aside by 0.038 W.
  **Dated note, Mon 2 Nov 2026 (Q136, E131):** card 1's automatic slope read 0.4008 W/°C again (E112(b) 0.4172), its fourth
  reading near 0.40–0.42 since 31 October. Frozen at 0.2414, E131's session tie to E82 passes, and its card scale moves with the
  slope: 1.0238 frozen, 1.0442 at the session's own, outside the band at 0.545 W/°C.
- **The launch-reading rule now skips runs** (1 November 2026). E78's runner skips an item whose die reading has not come
  back to its launch reading in the wait, which low-power tiles trigger: 5 of 265 in E95, one pass each of E103's largest and
  third-largest misses, `fp16.z_sub` in E104, which left it no interval. A retry needs its own registration. On aifoundry1's card
  1 a run takes 8.9 s, not 10.2 s, with 2 s quiet at 58 °C (E93), so budget by that.
- **A pass gate can void a registered minimum** (1 November 2026, Q133). E78's gates set aside 10912 in E109 (a random
  fp32 anchor spanning 1.067 W against 1.0, so two of three passes and NOT SCORED), 11510 and 11511 in E115 (board-meter
  dips; its primary kept one pass, and only the registered dips-removed fallback scored) and 11610 in E116 (the zero
  anchor), and the zeros-line gate set aside 11252 in E112 (so (b) NOT SCORED). On aifoundry3 the random-range gate had
  set aside one pass each in E86, E92 and E95. Register 4–5 passes, or how a set-aside pass is handled, and on aifoundry3
  a dips-aware gate.
  **Dated note, Mon 2 Nov 2026 (Q136):** on card 1 a pass with no hot anchor runs 2–3× its estimate. A launch on the cool die
  needed about three heats in E128 and 5–8 (median) in E129, whose anchors were cut to each format's zeros, so E128 kept two
  passes and E129 three of the six its R1 needed; E131's four passes, from a 50 °C die, took 547–652 s. On aifoundry3, E134's
  13410 was set aside on board-meter dips of 3–4 W, under E82 A2's 4 W line (its C1): register a dip rule that catches them.
  **Dated note, Mon 2 Nov 2026 (Q137):** on aifoundry3 E78's own pass gates set two of E140's four passes aside on readings the size of board-meter dips (a 2.489 W span of `fp32.randn`, a +0.715 W drift of `anchor_pi`), and two of its six power misses were dips on the kept passes (E140 D1, C2).
  **Dated note, Tue 3 Nov 2026 (Q138):** on aifoundry3 the random-range gate set E141's 14110 aside (`fp32.randn` spanning 1.704
  W, a dip's size), and E141's largest misses were single low passes (`fp32.lowrank2_w` read 22.33 W in one pass against 24.43 and
  24.50); E147 registered a 2 W dip line, under which none of its blocks was set aside, where E134's 4 W line would have set two A
  blocks aside. On card 1 a warm die makes passes short: E148's 14-run passes took 172–206 s with a median of one heat a launch,
  against 536–663 s for E129's on its cool morning; card 1's session-fitted leakage slope read 0.408 W/°C in E142's arm and 0.141
  W/°C on E148's low-power runs. Two A rows run on card 1 at the bench's 96 / 94 cycles an op (E148 R6).
  **Dated note, Tue 3 Nov 2026 (Q139):** a session's own leakage fit can be the noise: on aifoundry3 E152's `auto` fit read 0.308
  W/°C (E127 0.191, Q139(u)'s footing 0.2056), and at that slope the whole-degree window readings put ±0.3 W steps into quiet
  tiles' D; the footing's slope removes about 60% of the excess variance (E152 C5). E152's one config read of 19 returned no line
  within its 10 s timeout, and E78's launch gate skipped one anchor at a 59.0 °C die. On card 1 E157's pass gate set 15711 aside
  (`fp16.zeros` +0.384 W off its line); six pool-5 tiles re-run there a day apart reproduced their D to 0.1–0.2 W, not 0.05 (K1
  FAIL), where E153 reproduced E141's on aifoundry3 to 0.04 W on the footing; and card 1's zeros level, re-read on 3 November,
  read 1.833 W against 1.661 W frozen earlier (+10%).
- **A watcher can watch the wrong file** (2 November 2026, E139). During a pass the sampler writes `telemetry.jsonl.raw`; `telemetry.jsonl` appears only when the pass ends and is gzipped at once (`mf/block.sh`). E139's board-power watcher followed `telemetry.jsonl`, read no sample all session, and its test passed on a file of that name, so its registered 65 W stop was never armed (the die stop was; the board peaked at 53.52 W). Watch the `.raw` file, and test the watcher on a live pass (E139 C1).
- **A protocol's stops are armed only under its watcher's keys** (2 November 2026, E146). `run_hpl.py`'s watcher reads
  `safety.abs_stop_c`, `board_cap_w` and `cap_consecutive` (defaults 85 °C, 97 W and 3 samples); E136's `protocol.json` wrote its
  stops as `die_c`, `board_w` and `board_samples`, so E136 ran on the defaults, not its registered 80 °C and 93 W (it peaked at
  76.09 W, so no stop was needed). `run_e146.py` refuses a protocol whose stops lack the watcher's keys; the other runners' own
  abort keys were not checked (E146).
- **An in-run watcher that dates its lines must refuse a stale one** (2 November 2026, E148 C7). E142's watcher, copied into
  E145's and E148's runners, computes each sample line's age and never acts on it, so a sampler that died mid-run would go unseen
  for up to one run before `run_e78`'s 3 s check between launches stopped the pass; it did not happen (E148's largest gap between
  samples was 101 ms). Stop on a line older than about 1 s.
- **A file tile's C is not checked** (E80, E143). `sparsity_host --values file:` reports every launch "unchecked" (`main.cpp:589`,
  `:614`), so a file-tile run counts launches by completion, every hart reporting and no tensor error; say so in the registration
  (E143's departure).
  **Dated note, Tue 3 Nov 2026 (Q139's records):** it is checked now. Q139(k)'s host-side reference
  ([`tools/claims-v3/ccheck/`](../../tools/claims-v3/ccheck/README.md)) and its two-flag host patch log and check every launch's C
  bit for bit, and every launch of E153, E154, E157, E160 and E161 passed. Use `--c-poison` (without it a skipped store after a
  launch of the same length reads PASS), match each SPARSITY line to its C record, and count only a bit-exact PASS: a launch with
  the tensor mask on or B streamed reads UNMODELLED. The log adds a 1 MiB read a launch (and a 1 MiB write with the poison), which
  counts against a governed run's budget; E153's duty read 0.9932 against E141's 0.9963.
- **aifoundry2's admission estimate reads random-like fp32 low** (2 November 2026, E143, as in E105). The estimate built from M7's
  D on aifoundry3's footing put `fp32.wideexp48_dense` at 84.34 W; it drew 1.7–3.6 W more, peaking at 87.95 W, 5 W under E143's 93
  W stop. Size an aifoundry2 table with a margin over the estimate, or with a measured probe.
- **`fit_m6.heat_rows`' run length can span a heater launch** (2 November 2026, E142, post hoc). It takes a run's length from the
  next run's record (its `prev_end_ms` less this run's `t0_ms`), and on a cool int8 tile the next device process is often a heater
  launch, so three of E142's int8 tiles read 7.1–7.2 s and that arm's int8 heat rms read 1.29 °C, an artefact; with M7's own 5 s
  row rule the term reads 0.131 / 0.110 / 0.176 °C, and read from each run's own marks it moves the other way, so its run-length
  slopes are no run-length law. Cap the length as M7's rows do (5 s).
- **A scorer's two-pass minimum counts entries, not passes** (3 November 2026, E153 C1). Listing one pass twice let E153's
  registered scorer print every verdict at 16:40:11, before amendment A1; count distinct passes, and disclose any such look with
  its printouts.
- **A day post's plan text lags its save** (3 November 2026, E151, E152, E157, E159). After a save, `delete_msg.mjs --plan`'s text
  field still showed the previous source, so a rewrite built from it meets exit 7 under `EXPECT_TEXT` (a refusal, never a wrong
  save); rebuild from the edit box's text.
- **A session can stop with a finished run uncollected and its claim held** (3 November 2026, E160). E160's detached queue ended
  on aifoundry2 at 07:12:39, the card free, 34 minutes before the session that started it stopped on a usage limit; its data
  waited on the box until a resumed lane collected it read-only at 15:56, and its clause stayed in the day's first post, which
  someone else later deleted. Collect and release as soon as the queue ends, keep the collector beside the run so a resumed lane
  can collect without opening the device, and say in the records when a claim was left held.
- **A residency read of a state the build does not have raises SP errors** (1 November 2026, E77 and Q134(a)). On BL2 0.22.0
  raw states 4–6 are no state: each read fails (rc −5), logs two SP ERROR lines and pushes two `SP Runtime Error` events to
  the host, where a session that counts kernel events will see them. Every lab session that read residency since 27 October
  but E77 asked for states 2–6 (701 of aifoundry2's 712 reads, all 63 of card 0's), and those reads account for all but six
  of aifoundry2's 4,234 such events and all 378 of card 0's. Ask for raw states 2 and 3 (POWER_DOWN, POWER_SAFE); the lab's
  `ettelem-dv2` builds refuse raw 1 outright, so a POWER_UP read needs a new build.
  **Dated note, Mon 2 Nov 2026 (Q136(w)):** five lines in the lab's code still ask raw 4–6 (`dv2lib.sh:177`, `dv2/z2.sh:73`,
  `hpl/run_hpl.py:622`, `knob/run_knob.py:658`, `e77/run_e77.py:686`), and Q136(w)'s checker refuses them before a run; a
  runner that reuses one patches the call, as E119's `patch_residency` does, and declares it. No Q136 card run sent a residency
  read: E126's tool refused all 51 queries before it opened the device, and E133's wrapper answered them unsent.
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
  **Dated note, Sun 1 Nov 2026 (week 44), Q134's records:** that first query is a PMIC command. At et-platform `836a4ab` it
  writes the PMIC's firmware-management command register twice (E114's C1), a PMIC command by E85 C1's standard, and the
  lab's rule allows no PMIC command but the samplers' statistics reset. Take a card's identity by its module uptime
  (`DM_CMD_GET_MODULE_UPTIME`, a RAM read) and its unbroken continuity, as E77, E118 and E120 did; read the firmware release
  only when the owner allows that command.
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
