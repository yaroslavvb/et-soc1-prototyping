# Q132(g): the governor's open items, from what is already committed (Sun 1 Nov 2026, week 44, desk only)

*Written 00:00-01:00 PDT, Sun 1 Nov 2026. **No card was opened for anything here.** Host-side reads on aifoundry1-3 were read-only (`/sys`, the kernel log, `sensors`, the
boxes' own 5 s history). Everything is post hoc: nothing here was registered before the data, so these are readings, not verdicts. The one new test it led to, E100, is pre-registered
separately. Items are numbered as in section 11 of the kinds page, version `df55db86ada8`.*

## Results first

1. **Item 1, the alarm: aifoundry2 does not act on the reading that trips card 0.** Its power controller read 75 W or more 2,891 times in 93 runs, up to **88.88 W**, for up to
   1.5 s at a stretch. No alarm line in 300 rings, no 300 MHz reading in 120,366, and the host driver's PMIC event counter reads **0** since its 26 Oct boot, against **177** on
   card 0, all inside E84's fp32 random-data runs. The public register format cannot hold a set point above 78.75 W, so "set higher" is out. What was measured per card: PMIC 1.6.1
   alarms; PMIC 1.5.0 does not at 80-88 W. Not tested: the slow average, which the 65 W arm never let past 68.91 W. [§a](#a-does-aifoundry2-have-card-0s-75-w-alarm-item-1)

2. **Item 10, the idle reset: the cause is the Master Minion's one-second heartbeat reading "no kernel in use" in the gap between two kernels.** It is not a property of the data. 25 falls in six
   sessions each land within 14 ms of a kernel's start, with the kernel before at full clock. On a 1000.010 ms lattice fitted session by session on 16 of them (E80, E83, E87), 18 of the 24 kernel boundaries within 1.2 ms
   fell and **0 of the other 8,365** did. The same lattice predicts the fall at **502 of 505** gaps between processes it was never fitted on. Time since launch, die, power, format,
   session position and the statistics reset add nothing. E100 tests it with controlled gaps. [§b](#b-the-one-second-idle-reset-item-10)

3. **Item 9, the drift: it tracks the room, and most of "23 to 31 October" is the time of day.** All three boxes share a daily cycle: at rest aifoundry2's die reads 46.1 C at 11:00 PDT and
   49.6 C at 20:00 PDT. E64 ran at 20:37 on a warm evening, E80 at 12:22 near the low. Over four sessions on shared kinds the 76 s die line moves **+0.25 ± 0.07 C per C of rest die**, and
   a slope fitted on 31 Oct alone gives E64 +0.65 ± 0.42 C against +1.12 ± 0.33 measured. n = 4, post hoc: E98 tests it overnight. [§c](#c-the-heat-paths-drift-looking-back-item-9)

4. **Item 1, Horace He's pair: his code says `torch.bfloat16` at 8192 x 8192 x 8192.** His gist `mm_weird.py`, posted the day before the article and linked to it, sets both. So the 16-bit reading
   no longer rests on utilisation alone. But the gist's printed runs and the article's chart give zeros/randn of **1.21-1.22**, not the text's 295/257 = 1.148. [§d](#d-horace-hes-pair-item-1)

## (a) Does aifoundry2 have card 0's 75 W alarm? (item 1)

E84's reader ([`tools/claims-v3/kspeed/e84/posthoc_pmic_e84.py`](../../../../tools/claims-v3/kspeed/e84/posthoc_pmic_e84.py)) over every committed ring, with the power readings beside it
([`pmic_check.py`](pmic_check.py), [`pmic-check.txt`](pmic-check.txt), [`pmic-check.json`](pmic-check.json)):

| session (card) | rings | alarm lines | safe-state records | 300 MHz points | readings | at 300 MHz | max `board_w` | max average `sp.board_avg_w` | readings ≥ 75 W | runs ≥ 75 W | longest ≥ 75 W |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| E64, 23 Oct (aifoundry2) | 47 | 0 | 0 | 0 | 20,024 | 0 | 88.38 | 68.91 | 399 | 22 | 1.3 s |
| E69, 27 Oct (aifoundry2) | 31 | 0 | 0 | 0 | 6,540 | 0 | 86.61 | 68.01 | 99 | 7 | 1.4 s |
| E80, 31 Oct (aifoundry2) | 57 | 0 | 0 | 0 | 24,221 | 0 | 88.09 | 68.72 | 249 | 8 | 1.4 s |
| E83, 31 Oct (aifoundry2) | 118 | 0 | 0 | 0 | 48,344 | 0 | 88.88 | 68.79 | 1,213 | 30 | 1.5 s |
| E87, 31 Oct (aifoundry2) | 47 | 0 | 0 | 0 | 21,237 | 0 | 88.54 | 68.66 | 931 | 26 | 1.3 s |
| **aifoundry2, all** | **300** | **0** | **0** | **0** | **120,366** | **0** | **88.88** | **68.91** | **2,891** | **93** | **1.5 s** |
| E84, 31 Oct (aifoundry1 card 0) | 35 | 23 | 19 | 18 | 13,543 | 436 | 75.12 | 66.10 | 2 | 1 | 0.2 s |

`board_w` is the PMIC's instantaneous input power as the SP last read it, at 10 Hz. For 23 of aifoundry2's 93 runs the ring reaches back to the previous dump, so nothing could have been overwritten.
In the others the ring covers the run's end, and on card 0 the alarm repeats about every 1.1 s, so it would still show. E69's `sp.board_max_w` reads 88.54 W, but that running maximum was set before E69's
sessions, so its own highest reading is the 86.61 W above.

**A count the rings cannot miss.** The driver counts each PMIC event in sysfs (`err_stats/ce_count`, `PmicCeEvent`; `et-driver/et_event_handler.c:664-668`).
Read at 00:13 PDT on 1 Nov ([`host/`](host/)), since each box's boot on 26 Oct:

| card | PMIC firmware (read) | `PmicCeEvent` | reached 75 W since that boot? |
|---|---|---:|---|
| aifoundry2 | 1.5.0 (E69) | **0** | yes: E69, E80, E83, E87, up to 88.88 W |
| aifoundry1 card 0 | 1.6.1 (E84 A1) | **177** | yes: 75.12 W read, and the alarm's own value 75.00-76.75 W |
| aifoundry3 | 1.5.0 (E79) | 0 | no: pinned at 600 MHz, 56.43 W at most in 31 Oct's sessions ([`other-cards-max.txt`](other-cards-max.txt)) |
| aifoundry1 card 1 | 1.3.0 (E82 A1) | 0 | no: it stays at 600 MHz, 61.30 W at most in 31 Oct's sessions |

All 177 are in the kernel log as "Power Overshoot Beyond Threshold", at 15:44 (5), 15:47 (7), 16:02-16:05 (165), which are E84's four fp32 random-data runs (15:44:23, 15:47:30, 16:02:22, 16:03:48)
([`host/err2-aifoundry1.txt`](host/err2-aifoundry1.txt)). E84's README gives 75.00-76.25 W, from what its rings kept; the driver's log holds all of them and reaches 76.75 W.

**What the public firmware says, and where it stops** (`aifoundry-org/et-platform` at `836a4ab`). All four cards report BL2 0.22.0 (no build hash is exposed).

- At the end of boot the SP calls `pmic_set_tdp_threshold(75)` (`device-bootloaders/src/ServiceProcessorBL2/common/main.c:552`, `device-bootloaders/src/ServiceProcessorBL2/driver/pmic_controller.c:503-516`).
- The register is one byte: 15 W plus 0.25 W per count, so 78.75 W at most, and the setter caps at 78 W (`pmic_controller.c:2157-2224`, `pmic_hal.h:1009-1010`). A set point above 88.88 W cannot be written in this format.
- On an interrupt the handler reads the cause, calls back into POWER_SAFE, 300 MHz, and pushes an event to the host (`device-bootloaders/src/ServiceProcessorBL2/driver/pmic_controller.c:752-781`, `device-bootloaders/src/ServiceProcessorBL2/services/thermal_pwr_mgmt.c:2172,2317`).
- The PMIC's own firmware, which decides when to interrupt, is not in the public tree.

**Verdict.** The reading reached 75 W on aifoundry2, thousands of times, with no alarm. So the alarm is absent on this card, or does not compare this reading. It is not "untested".

**Limits.**
- One card against one: PMIC 1.5.0 and 1.6.1 are also different boards, and nothing recorded separates firmware from board. Recorded identity is thin: `Form Factor: PCIE` on the cards read, and every host board is the same model ([`host/boards.txt`](host/boards.txt)).
- aifoundry3 and aifoundry1 card 1 have not reached 75 W, so they are untested.
- The average never passed 68.91 W, so an alarm on the slow average is not excluded. On card 0 the average peaked at 66.10 W, so card 0's alarm does not use it.

**What a card run would have to do to finish it.** Only the slow-average case is left, and it needs a governor move, which this run forbids: under the field manual's gates, raise the TDP to at most 75 W and burst fp16 random
data (76.1 W at 800 MHz, E80) from a cool die, so that the average passes 75 W inside the 85 W abort, then read the rings and `PmicCeEvent`. Reading the set point directly would be a PMIC command. For the blog neither is needed: on aifoundry2 the two limits are the only limits seen.

## (b) The one-second idle reset (item 10)

### The code path, public source (`aifoundry-org/et-platform` at `836a4ab`)

1. The Master Minion runs a periodic heartbeat. It sends `event.state = KW_Get_Kernel_State()`, a snapshot of that instant (`device-minion-runtime/src/MasterMinion/src/services/sp_iface.c:76-100`, set up at `:1075-1095`).
2. The snapshot is busy only if a kernel slot reads `KERNEL_STATE_IN_USE` (`device-minion-runtime/src/MasterMinion/src/workers/kw.c:1915-1930`). A slot becomes `IN_USE` only after the launch's multicast has been acknowledged (`:938`) and is freed at completion (`:1653`). Between two kernels the snapshot reads idle.
3. The SP passes it on (`device-bootloaders/src/ServiceProcessorBL2/rtos_task/command_dispatcher.c:476`). On any busy-to-idle edge, `Thermal_Pwr_Mgmt_Update_MM_State` notifies POWER_IDLE at once, with no debounce (`device-bootloaders/src/ServiceProcessorBL2/services/thermal_pwr_mgmt.c:3110-3124`).
4. POWER_IDLE sets the boot point, 600 MHz (`:2177-2180`, `:1980-1985`), the PLL first and the voltage after, then the trace record (`:1832-1856`).
5. The power branch climbs only while the state is not idle (`:879-880`, `:910-919`), so the clock waits for the next heartbeat, then climbs a point per pass.

The firmware programs the heartbeat as 100 software-timer ticks; the rings measure the period, below. The cards report minions 0.25.1, and the public tree's changelog tops out at 0.24.0 plus unreleased work, so the running binary was not read.

### What the data show

Hits are found two ways ([`ir_hits.py`](ir_hits.py), [`ir-hits.txt`](ir-hits.txt)): the sampler (a 600 MHz reading straight after 800 MHz, E80's rule) and the kernel's own counters (a kernel at 0.55-0.62 GHz straight after one at 0.79 GHz or more). 25 falls in six sessions:

| session | card | kernel boundaries at 800 MHz | falls | expected, 2 ms in 1000.01 ms | 95% interval of the count |
|---|---|---:|---:|---:|---|
| E64 | aifoundry2 | 1,141 | 2 | 2.3 | 0.2-7.2 |
| E69 | aifoundry2 | 616 | 2 | 1.2 | 0.2-7.2 |
| E80 | aifoundry2 | 2,070 | 5 | 4.1 | 1.6-11.7 |
| E83 | aifoundry2 | 5,096 | 7 | 10.2 | 2.8-14.4 |
| E87 | aifoundry2 | 1,223 | 6 | 2.4 | 2.2-13.1 |
| E84 | aifoundry1 card 0 | 1,635 | 3 | 3.3 | 0.6-8.8 |
| **all** | | **11,781** | **25** | **23.5** | **16.2-36.9** |

([`ir-tests.txt`](ir-tests.txt)). The 2 ms comes from the falls' own spread; the host's mean gap between kernels, 1.29 ms, is a floor, and gives 15.2. E83's `BURST-06-fp32-randn_large-r1` is flagged by the sampler rule and left out: its kernel before ran at 0.63 GHz, inside the power arm's dither. E84's two 300 MHz cases are the alarm, above.

1. **Every fall lands at a kernel's start.** The hit kernel ran at 800 MHz for at most 13.9 ms before falling (median 3.9 ms, on the 21 sampler-rule falls), in kernels 473-644 ms long, and the kernel before ran its whole length at 0.7998-0.8002 GHz. One fall on a kernel's counters has about a 3% chance of doing that by accident. (One of the four kernel-rule falls reads x = -26 ms: E87 `SUS-08-int8-real-l6_attn_qk-r1`, kernel 1, 0.62 s into its process, whose kernel ran longer than a plain 600 MHz kernel, so the two-clock estimate does not apply to it. Its kernel before ran at 0.7998 GHz, and its start sits +0.4 ms from the lattice.)

2. **The falls sit on one lattice** ([`ir_lattice.py`](ir_lattice.py), [`ir-lattice.txt`](ir-lattice.txt)):
   - Period fitted on each session's sampler-rule falls, on the host clock: E80 1000.0102 ms (5 falls, rms 0.63 ms), E83 1000.0098 ms (6, rms 0.50 ms), E87 1000.0105 ms (5, rms 0.67 ms). Three separate fits agree to 0.0007 ms.
   - On the SP's own tick, every POWER_IDLE record in a session's rings, ordinary end-of-process idles included, lines up at 0.999994-1.000003 s, circular R 0.979-0.996 in six sessions.

3. **The boundaries not hit fit too.** Boundaries at 800 MHz, by distance of the kernel's start stamp from that lattice:

   | session | within 1.2 ms: boundaries | fell | further: boundaries | fell |
   |---|---:|---:|---:|---:|
   | E80 | 5 | 5 | 2,065 | 0 |
   | E83 | 12 | 7 | 5,084 | 0 |
   | E87 | 7 | 6 | 1,216 | 0 |
   | **all** | **24** | **18** | **8,365** | **0** |

   The hits fix the lattice, so the test is the rest: none of 8,365 boundaries fell, and two falls not used in any fit (E83 at 0.0 ms, E87 at +0.4 ms) land inside the zone. The stamps are whole milliseconds, which blurs the zone's edge by about 0.5 ms, so 6 unfallen boundaries inside it are expected.

4. **Gaps between processes are the same test, out of sample** ([`ir_gaps.py`](ir_gaps.py), [`ir-gaps.txt`](ir-gaps.txt)). When a process ending at 800 MHz is followed by another, the card sees 197 ms with no kernel (330 ms on aifoundry1). The lattice predicts which gaps hold a heartbeat:

   | | clock fell | clock stayed |
   |---|---:|---:|
   | a lattice point in the gap | 91 | 2 |
   | none in the gap | 1 | 411 |

   That is **502 of 505**. E80, E83 and E87 use lattices fitted only on mid-launch falls. E64, E69 and E84 have 2-3 falls, all of which fix the period, so theirs is out of sample for the gaps too. The three misses are edge cases: two lattice points within 0.9 ms of the kernel's end, and one 15.8 ms into the next process, at the calibration kernel's own boundary. Share of gaps holding a heartbeat: aifoundry1 22 of 72 for its 330 ms; E83 45 of 228 for its 197 ms.

5. **The climb waits for the same heartbeat.** For first processes with no limit in reach, the first 800 MHz reading scatters from process start, but not from the first heartbeat inside a kernel:

   | | first processes | from process start: median, sd | from that heartbeat: median, sd |
   |---|---:|---|---|
   | E80 | 56 | 1.02, 0.36 s | 0.31, 0.055 s |
   | E83 | 117 | 0.93, 0.32 s | 0.32, 0.052 s |
   | E87 | 46 | 0.93, 0.28 s | 0.29, 0.052 s |

   This is what "launch to 800 MHz a median 0.67 s, at most 1.2 s" was. E80's long late ramp (first 800 at 2.53 s) is the one whose first lattice point fell outside a kernel, so it waited a whole second more.

6. **A fall lasts one heartbeat.** First 600 reading to first 700: median 1.10 s, range 1.00-1.20; to first 800: 1.30 s, range 1.20-1.40 (20 falls that recovered inside their process). That is the "about a second". Lost work: about 0.3 s at 800 MHz per fall, which is the 43-45 MHz a 6 s burst lost in E80.

### The simple hypotheses, against the boundaries not hit

Hits against each one's share of the 11,781 boundaries, Monte Carlo over 20,000 placements ([`ir_tests.py`](ir_tests.py), [`ir-tests.txt`](ir-tests.txt)). Uncorrected; nine tests, so one near 0.05 is expected.

| hypothesis | p | reading |
|---|---:|---|
| time since the process started | 0.14 | falls from 0.6 to 8.1 s |
| position in the session | 0.65 | |
| die temperature | 0.91 | falls from under 56 C to over 64 C |
| board power | 0.93 | falls from under 36 W to over 62 W |
| number format | 0.49 | int8 14, fp32 6, fp16 5 |
| block (burst, sustained) | 0.16 | |
| session | 0.25 | E87 runs high, E83 low, each inside its interval |
| hour of day | 0.048 | carried by 3 falls at 18-20 h; hour is also session here |
| length of the kernel before | 0.12 | |

**The statistics reset, which E85 linked post hoc.**
- E64, E69, E80, E83, E84 and E87 sample without it and have the falls: 0.32-1.14% per heartbeat at 800 MHz.
- The camera runs, with `--reset-ms 1000`, read 0.13-0.41% per second of work ([`ir_camera.py`](ir_camera.py), [`ir-camera.txt`](ir-camera.txt)). No rise.
- Their mid-launch falls sit at one phase, the same as that session's ordinary end-of-process falls: E63 s1 0.277 and 0.282, E63 s2 0.401 and 0.406, E73 0.807 and 0.813, E85 0.202 and 0.190 of a second (R 0.97-0.99). These runs start a process on a fixed 10 s grid, so the heartbeat keeps its place inside every process. That is why E63 s1's falls all came at 7.2-7.3 s, and E85's at 3.2, 4.2 and 7.2 s.
- E85's "late ramps" were a threshold. Its first 800 reading has three modes: 0.3-0.7 s (45 launches), 1.3-1.6 s (192), 2.3-2.5 s (3). The 1.5 s check cuts through the middle mode, and 20 of its 23 "late" launches are that mode's tail. A reset does slow a climb: tail launches read 13 of 47 right after a reset, 7 of 193 otherwise (one-sided Fisher p 3.7 × 10⁻⁶). The whole-second misses show nothing: 0 of 47 against 3 of 193 (p 1). So a reset can delay the SP by a fraction of a pass. It does not cause a fall.
- The slow sampler command at a fall (median 92 ms against 22 ms on the reading before) comes with the fall and not before it, which fits the SP being busy changing the operating point.

**Periodic SP tasks.** The falls line up on 1 s and on nothing shorter; the SP's own passes run about every 0.2 s.

### How sure, and what would settle it

Very sure of the mechanism for these sessions: 0 of 8,365 and 502 of 505 leave little room. Still post hoc, on a chain read from public source and not from the cards' binary, with the zone's width taken from the same falls. **The test is E100** ([`tools/claims-v3/e100/`](../../../../tools/claims-v3/e100/README.md), pre-registered in `5e12c4bd`; its data go to `2026-11-01-e100-idle-reset/`): on aifoundry2, on int8 zeros at about 35 W, random added gaps averaging 0, 5, 20 and 100 ms between 338 ms kernels, and one 4 s kernel with no gap inside. It predicts 0.9, 3.6, 8.4, 29.0 and 0 falls in 144 heartbeats, with a small host change and about 30 card-minutes.

## (c) The heat path's drift, looking back (item 9)

### The record

A record nobody had used: `tools/lab/live/live-collector.py` writes `~/live/history/<UTC date>.jsonl` on each box, every 5 s, with `temps.{nvme,nic,cpu}`, `load` and each free card's die and W, and keeps nine days. Copied on 31 Oct ([`live-history/`](live-history/), numbers only), it reaches back to 22 Oct 17:00 PDT, before E64.

### All three boxes share one daily cycle

| hour (PDT) | aifoundry2 idle die | idle W | aifoundry3 idle W | a3 NVMe | a2 NIC | outside air, C |
|---|---:|---:|---:|---:|---:|---:|
| 00 | 48.45 | 22.50 | 23.82 | 38.24 | 45.88 | 11.5 |
| 04 | 47.48 | 22.26 | 23.62 | 37.47 | 45.04 | 10.2 |
| 08 | 46.54 | 22.03 | 23.39 | 36.72 | 44.10 | 11.1 |
| **11** | **46.08** | **21.94** | 23.33 | 36.60 | 43.74 | 17.0 |
| 14 | 47.93 | 22.36 | 23.74 | 37.64 | 45.26 | 20.2 |
| 16 | 49.54 | 22.76 | 24.22 | 38.53 | 46.77 | 19.2 |
| **20** | **49.59** | **22.77** | 24.15 | 38.66 | 46.80 | 13.7 |

Nine-day means with the card idle at least 30 min ([`room-proxies.txt`](room-proxies.txt)). The other readings follow aifoundry2's idle W at r 0.90-0.98: a2 NIC 0.978, a2 NVMe 0.955, a1 card 0's die 0.951, a1 card 1's die 0.942, a3's W 0.923, a1 NVMe 0.922, a1 NIC 0.919, a3 NIC 0.903, a3 NVMe 0.899. Outside air (Open-Meteo's hourly model at the lab's coordinates, not a station there) reads r 0.11 in phase and **0.735 with the air leading by 5 hours**. The rest reading tracks the room or the building, not the air directly. On the same day, 23 Oct, the rest die read 46.1 C at 12:55 (E63) and 49.3 C at 20:37 (E64).

### The die lines against the room at rest

([`die_lines.py`](die_lines.py), [`drift_paired.py`](drift_paired.py), [`die-lines.txt`](die-lines.txt), [`drift-paired.txt`](drift-paired.txt)). The room is read 30-5 min before each session's first run. Offset is die minus 0.4573 W, the pooled within-session slope.

| session | card | first run (PDT) | free line (C, per W) | 65.5 C at | offset | rest W | rest die | a2 NIC | a2 NVMe | shift from E80, shared kinds |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| E80 | a2 | Sat 31 Oct 12:22 | 42.23 + 0.4349 | 53.5 W | 41.11 | 21.76 | 45.58 | 43.20 | 36.17 | 0 |
| E83 | a2 | Sat 31 Oct 13:46 | 40.76 + 0.4631 | 53.4 W | 41.03 | 22.03 | 46.42 | 43.99 | 36.90 | −0.10 ± 0.20 (5 kinds) |
| E87 | a2 | Sat 31 Oct 19:49 | 41.69 + 0.4562 | 52.2 W | 41.63 | 22.17 | 47.15 | 44.81 | 37.90 | +0.41 ± 0.20 (5 kinds) |
| E64 | a2 | Fri 23 Oct 20:37 | 41.88 + 0.4696 | 50.3 W | 42.44 | 22.69 | 49.28 | 46.59 | 39.34 | +1.12 ± 0.33 (5 kinds) |
| E69 | a2 | Tue 27 Oct 14:24 | four cells under moved limits, not a line | | 41.47 (control cell) | 22.10 | 46.67 | 44.42 | 37.55 | no shared kind with E80 |
| E84 | a1 c0 | Sat 31 Oct 15:43 | 41.78 + 0.4753 | 49.9 W | 42.49 | 18.79 (its own) | 47.68 (its own) | a2 at that hour: 44.53 | 37.82 | another card |

Against each reading at rest, through the origin and weighted (E80 is a common baseline, so the points are not independent):

| reading | slope, C of line per unit | on 31 Oct alone | E64 predicted by that (measured +1.12 ± 0.33) |
|---|---:|---:|---:|
| a2 idle die | 0.256 ± 0.070 | 0.177 ± 0.114 | +0.65 ± 0.42 |
| a2 idle W | 0.951 ± 0.269 per W | 0.595 ± 0.416 | +0.55 ± 0.39 |
| a2 NIC | 0.268 ± 0.074 | 0.181 ± 0.114 | +0.61 ± 0.38 |
| a2 NVMe | 0.272 ± 0.075 | 0.181 ± 0.108 | +0.57 ± 0.34 |
| a1 card 0 idle die | 0.305 ± 0.084 | 0.202 ± 0.121 | +0.56 ± 0.34 |

**Does the drift track a proxy? Yes, within what four sessions can show, and they cannot tell the proxies apart.** E64 ran at the warm end of the cycle on a warm day, 3.7 C of rest die above E80. Comparing by hour, E64 against E87 (both about 20:00) leaves +0.59 ± 0.13 C for 2.13 C of rest die. Nothing here calls for a change in the path itself. The "3 W at the trip" is the slope of the line turning 1.38 C into watts.

**Near-steady points agree in sign, and are steeper.** E63, E73 and E85 hold one 10 s pattern for 30-45 min, so the die settles ([`camera_lines.py`](camera_lines.py), [`camera-lines.txt`](camera-lines.txt)): offset 39.30 at rest 46.11 (E63 s1, 256 minions), 40.14 at 47.09 (E73), 40.06 at 47.55 (E85). That is about 0.5-0.9 C per C, against 0.25 for the 76 s runs, which start from a die gated at 55-57 C. Two differences, rough, and the two geometries differ. E98's long hold is the test.

**At the trip the shift is bigger in speed.** fp16 ones: 737 MHz at 49.3 W in E64, 782 MHz at 53.2 W in E80, so about 12 MHz and −1 W per C of rest die. That is the "sustained speed of a borderline kind depends on the card's cooling that day" of E80.

**Card 0.** E84's "1.1-1.5 C hotter per board watt" compared an afternoon with aifoundry2's noon and early afternoon. Corrected at 0.25 C per C of aifoundry2's rest die it is about 1.0-1.3 C, still hotter.

**Other readings tried.**
- The camera's own thermistors at four session starts show no pattern ([`cam_scene.py`](cam_scene.py), [`cam-scene.txt`](cam-scene.txt)).
- `acpitz` is a constant on all three boxes (16.8 and 27.8 C).
- `sar` holds no temperature group.
- The card's own system temperature reads 0 (`14-card-behaviour.md`).
- The host boards' sensors are out of reach as they stand: `gigabyte_wmi` is loaded but gives no hwmon device, and `it87` is not loaded ([`host/boards.txt`](host/boards.txt)). Neither was changed.
- A real inlet reading needs a thermometer at the card, which only someone in the lab can add.

**The best proxy tonight**, and what E98 should log, is in [`e98-spec.md`](e98-spec.md): the card's own idle W and die in the last 60 s before each probe after at least 15 min of rest, NIC at rest beside it, and all three boxes' 5 s history pulled at the end. Idle W is the sharp one: 0.2315 W per C, r 0.978, 0.01 W resolution. It forgets a session within 5 min, NIC within 15 ([`rest-decay.txt`](rest-decay.txt)).

## (d) Horace He's pair (item 1)

Horace He's post gives no dtype, and its zeros/randn snippet uses a bare `N` ([post](https://www.thonking.ai/p/strangely-matrix-multiplications)). His code does:

- **Gist** [`Chillee/42e4635c`](https://gist.github.com/Chillee/42e4635c59760a74cb3b4ba7ea5ad9f8), created 28 Apr 2024, the day before the post; its description is the post's title and link. GitHub's API names the account Horace He. `mm_weird.py`: `M = 8192`, `N = 8192`, `K = 8192`, `f(M, K, dtype=torch.bfloat16)`, `flops = ... * 2`, median of 10 shuffled trials, on `torch.mm`. His other matmul gists use `torch.bfloat16` too (`abc38703`, `2ec89696`).
- That fits 258 TFLOPS being "83% flop utilization" of the A100's 16-bit peak, the reading Q130(e) rested on. It is now from his code as well.

**But the script's own recorded output is not 295 / 257:**

| source | randn | twos | sparse | one bit | rand | zeros | zeros / randn |
|---|---:|---:|---:|---:|---:|---:|---:|
| gist comment, 28 Apr 2024, image | 239.41 | 287.43 | 257.72 | 287.80 | 251.97 | 292.30 | **1.221** |
| gist comment, 21 Jun 2024, "reran it on an A100", image | 240.43 | 288.60 | 256.18 | 286.87 | 251.62 | 291.63 | **1.213** |
| the article's text | 257 | | | | | 295 | **1.148** |

The article's unlabelled chart, read from its pixels ([`horace_chart.py`](horace_chart.py), [`horace-chart.txt`](horace-chart.txt), about ±0.1 TFLOPS): Randn 236.47, Checkerboard 242.43, Sparse 245.22, Rand 247.33, Ternary 263.67, One Bit 282.02, All Pi 286.82, Twos 287.11, Zeros 287.69, so **1.217**. That supersedes `2026-10-31-q130-literature/README.md` §7's "nothing quantitative can be quoted" for those kinds. The sparse kinds differ between his scripts: `mm_weird.py` zeroes the negative half, `sustainable_clock_speed.py` keeps a random tenth, and the article describes 75% masked.

**Not stated anywhere I searched** (the post, its footnotes and comments, his gists, GitHub): that the text's 295 / 257 came from this script. The 257 is also the text's CUTLASS number just above it. Comment threads add two loose ends: one reader's H100 runs of the same script read randn 1015-1055 against zeros 806-815, the reverse order, which Horace He answered was "quite strange"; and on AMD parts a reader reports zeros at 1.21x and 1.35x of normal data, with its own code.

**The one question Yaroslav could ask him** (nobody was contacted): *"Your gist's `mm_weird.py` is bfloat16 at 8192³ and prints zeros 292 / randn 239, and the chart says 288 / 236. Did the post's 295 / 257 come from that script, or from another run?"*

## What this closes, narrows or leaves open (section 11 of the kinds page)

- **Item 1, narrowed twice.** The format and size now have a source (his code), but the pair's 1.148 has a question beside it. aifoundry2's alarm moves from untested to not acting on the fast reading, and the slow average alone stays untested.
- **Item 9, narrowed, not closed.** The drift tracks the room at rest, on four sessions, post hoc. E98 is its test.
- **Item 10, a known cause with strong post-hoc evidence.** E100 is its test.

## What a blog reader can now be told

- A card's 75 W alarm is that card's: one card with PMIC 1.6.1 trips it, and aifoundry2 with PMIC 1.5.0 runs through 88.88 W without one ([`pmic-check.txt`](pmic-check.txt), [`host/`](host/)).
- The one-second dip has nothing to do with the numbers. A firmware heartbeat that looks once a second sometimes lands between two kernels and sees an idle chip ([`ir-lattice.txt`](ir-lattice.txt), [`ir-gaps.txt`](ir-gaps.txt)).
- It happens about once per 500 kernel boundaries, whatever the kind ([`ir-tests.txt`](ir-tests.txt)).
- The lab's room warms and cools by about 3.5 C of rest die each day, so a sustained speed near the trip depends on the hour ([`room-proxies.txt`](room-proxies.txt), [`drift-paired.txt`](drift-paired.txt)).
- Horace He's benchmark is bfloat16 at 8192³, from his own script ([gist](https://gist.github.com/Chillee/42e4635c59760a74cb3b4ba7ea5ad9f8)).
- His recorded runs put zeros about 21-22% above random data ([`horace-chart.txt`](horace-chart.txt), the gist's comments).

## Files

| path | what |
|---|---|
| `pmic_check.py`, `pmic-check.{txt,json}`, `other_cards_max.py`, `other-cards-max.txt` | item 1: rings and readings per session; the highest reading on the two cards that never reached 75 W |
| `host/` | read-only host reads of 1 Nov 2026: `err-<box>.txt` (driver counters, kernel-log kinds), `err2-aifoundry1.txt` (the alarm events' times and values), `boards.txt` |
| `ir_lib.py`, `ir_hits.py`, `ir_lattice.py`, `ir_gaps.py`, `ir_tests.py`, `ir_camera.py`, and their `.txt`, `.json` | item 10 |
| `die_lines.py`, `drift_paired.py`, `room_proxies.py`, `rest_decay.py`, `rep_noise.py`, `camera_lines.py`, `cam_scene.py`, and their `.txt`, `.json` | item 9 |
| `live-history/aifoundry{1,2,3}.tgz` | each box's `~/live/history/*.jsonl` as of 23:50 PDT, 31 Oct. Numbers only (`t`, `cpu`, `mem`, `load`, `temps`, `cards[].{n,ok,held,die,max,w}`) |
| `live-5min.csv` | the same as 5-minute medians |
| `open-meteo-sf.json` | Open-Meteo's hourly air temperature at the lab's coordinates |
| `e98-spec.md` | what E98 should log, as handed to its lane (the camera phone's address taken out) |
| `horace_chart.py`, `horace-chart.txt` | the chart's bars from its pixels; the image is not committed, its URL is in the script |
| `rebuild.sh` | every step below, in order |

Rebuild, from this directory, with Python 3 and no third-party modules: `bash rebuild.sh`. It unpacks `live-history/` into a scratch folder you name. `horace_chart.py` needs the image from the URL in its header. The `host/` files are reads of live state and cannot be rebuilt.
