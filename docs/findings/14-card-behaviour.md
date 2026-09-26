# Finding: how this card behaves, and how to measure it without fooling yourself

[← Findings index](README.md) · no single published page; the pieces are in
[Power and temperature](https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature) (A3), [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) (A4)
and [The ET-SoC-1's DVFS loop](https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage) (A11) · numbers and sources: [05-claims.md](05-claims.md)

**Sources:** E5, E6 (telemetry and rails), E9 (the protocol), E10 (the governor), E12 (long runs), E20 and E21 (the
second card, the three machines), E27 and E29 (the rails' filter, the meter traps), R3 (the firmware policy). For
25 September: the aifoundry1 investigation and fix ([troubleshooting report](https://spacesheep.dev/@yaroslavvb/aifoundry1-troubleshooting),
[fix log](https://spacesheep.dev/@yaroslavvb/aifoundry1-fix), evidence in
[`docs/reports/data/2026-09-25-aifoundry1/`](../reports/data/2026-09-25-aifoundry1/README.md)), the read-only audit
and the fixes of the three hosts that day, and the version-3 campaign's amendments A2–A5
([`AMENDMENTS.md`](../reports/data/2026-09-25-claims-v3/AMENDMENTS.md)).

Everything here was learned by getting it wrong first. If you are about to measure power or temperature on an
ET-SoC-1, read this before designing the experiment.

**Updated 2026-09-25.** The lab now has **four working cards on three firmware releases**, not two. Two statements
made here before that date were wrong and are corrected below: aifoundry1's cards were refused because of an empty
driver version string, not a `srcversion` mismatch; and aifoundry3's zero TDP is set by a boot service at every boot,
not flashed. Older files (05-claims.md, 03-experiments.md E21, 16-dvfs-and-leakage.md, the DVFS page, and the
others listed in [AGENT.md](../../AGENT.md), "Known stale spots") still carry the old wording until their next
revision; this file is the current one.

---

## The clock governor is thermal first

The [service processor](README.md#terms) runs a power-management task (`thermal_pwr_mgmt.c`, R3), once per
management pass of about 133 ms on aifoundry2 (aifoundry3's readings change only about every 250 ms). While a kernel is running it steps the minion operating point **down** if the
die's whole-degree reading is above a software threshold (**65 °C**) *or* the board's average power is above the
TDP level (**65 W**), and **up** otherwise. The thermal branch is checked first and wins. This is the firmware
source at `353f20e`; the cards' own trace strings match an older build (R3), so details may differ on the card.
[16-dvfs-and-leakage.md](16-dvfs-and-leakage.md) has the loop in detail.

This card's operating points, read from telemetry (E10):

| Point | Clock | Die voltage |
|---|---|---|
| lowest | 600 MHz | 516–518 mV |
| middle | 700 MHz | 568 mV |
| highest | 800 MHz | 618–620 mV |

**Consequence:** a card that has been busy usually idles above 65 °C (72–80 °C on 20–22 September; about 65 °C on
23 September, when the governor did intervene) and therefore runs *everything* at 600 MHz, whatever the power — which is why an earlier version of this work
concluded, wrongly, that "the clock never moves". It moves only from a cool die.

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

## The telemetry, and what each number really is

`tools/ettelem` reads the management library directly (`libDM.so`), which exposes more than the stock CLI:

| Field | Meaning | Gotcha |
|---|---|---|
| `board_w` | board power, 10 mW steps | refreshed once per service-processor pass, about every 133 ms on aifoundry2; on aifoundry3 the value changes only about every 250 ms (why is not established); near-instantaneous otherwise |
| `sp.minion_w`, `sram_w`, `noc_w` | per-rail power | **the PMIC's running average, roughly first-order with τ ≈ 1.15–1.22 s**: a step reaches 55–57% after 1 s, 83–84% after 2 s and about 94% after 3 s (E27, `catalogue.json` `rail_filter`, both cards), copied by the SP each pass (on aifoundry3 the copy changes about every 250 ms); not a moving average. Skip 2–3 s after any change before averaging. `ettelem sample --reset-ms` resets the statistics on a schedule, but whether that turns the average into a window mean is untested |
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
  the cause is on the card, its SP loop or its PMIC; which is not established.
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

Updated 2026-09-25: aifoundry1's two cards work since 15:02 that day, so there are four cards on three firmware
releases. Before using a card for anything comparative, read its governor configuration. Two read-only commands:

```
gcc -O2 -I/opt/et/include -o etcfg tools/etcfg/etcfg.c && ./etcfg   # the driver's view: TDP, boot clock, shire mask, cache sizes
LD_LIBRARY_PATH=/opt/et/lib build/ettelem/ettelem config           # the firmware's view: TDP, threshold, power state
```

On aifoundry1, prefix `ET_DEVICES=<n>` to address card n (below). `ettelem config` opens the management node, so
check first that nobody holds the card (`et-who`).

| | aifoundry2 | aifoundry3 | aifoundry1 card 0 | aifoundry1 card 1 |
|---|---|---|---|---|
| Firmware release (BL / PMIC / minion) | 1.3.1 (0.20.0 / 1.5.0 / 0.23.0) | 1.3.1 (the same) | 1.4.1 (0.21.2 / 1.6.1 / 0.24.0) | 1.2.0 (0.18.0 / 1.3.0 / 0.22.0) |
| TDP the driver reports | 65 W | 65 W | 65 W | 65 W |
| **TDP the firmware uses** | **65 W** | **0 W**, set at every boot (below) | 65 W | 65 W |
| Clock | firmware DVFS: 600, 700 or 800 MHz; above 600 only below about 68 °C | **600 MHz** (NoC 400), never seen higher (10 Hz telemetry) | firmware DVFS; **idles at 300 MHz** (`low_power`) | firmware DVFS; idles at 600 MHz (`managed_power`) |
| Idle | 31–36 W at 73–80 °C (27 W cold) | 23.6 W at 50 °C (25.1 W at 56 °C under the runs); the die idles at 55–57 °C since the host changes of 25 Sep | 18.6–18.8 W at 300 MHz; 26 W at 600 MHz | 33–35 W at 600 MHz and 57–62 °C |
| Use it for | the main card | compare switching power over idle, never absolute watts | **nothing sustained: it overheats** (below) | anything; it peaked near 71 °C under the campaign's smoke blocks |
| Version-3 campaign | yes | yes | excluded (amendment A4) | yes |

The hosts differ too. Host-side timing (launch, synchronisation, copies, compile times) is not comparable between
them; card-side numbers (cycles, power at a fixed operating point) do not depend on the host.

| | aifoundry1 | aifoundry2 | aifoundry3 |
|---|---|---|---|
| CPU, RAM, BIOS | i7-11700K (8 cores, 16 threads), 128 GB, F5 | i5-11600 (6 cores, 12 threads), 64 GB, F5 | i7-11700K, 32 GB, F6 |
| `/opt/et` runtime and device layer | a local build of an et-platform fork (May 2026): its `libetrt.so` and `libdeviceLayer.a` differ from the others; the device layer honours `ET_DEVICES=<n>` and takes the DRAM ranges from the driver. Older ET copies in `/usr/local/bin` (February 2026: `esperanto_flash_tool`, `profiler_converter`) come first on PATH | the stock et-platform `353f20e` build (December 2025), runtime 0.19.0 | `353f20e`, except `libetrt.so`: a patched Release `-O3` build of `836a4ab` (2026-07-23, an event-id guard) |
| The same on all three | the `et_soc1` driver 0.20.0 (one source since aifoundry1's fix), `libDM.so`, `dev_mngt_service`, `et-powertop`, and the RISC-V GCC 15.1, which generates identical code on all three (see Traps) | | |

**aifoundry3 is pinned at 600 MHz by a zero TDP.** The governor's step-down test is `measured power > TDP` and its
step-up test is `<`. At a TDP of zero the first is always true and the second never is, so the loop logs a
throttle-down at every kernel start, and nothing can ever step it up. The card's own log says so: `Power throttle
down event, current pwr 35380  tdp level: 0`, 26 times in one 8 KB window, alternating with idle events, with no
step-up event at all. A second reading agrees: `get_power_state()` classifies a card as `MAX_POWER` exactly when
power exceeds the TDP, and aifoundry3 reports `max_power` while drawing 23 W.

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
included. `tools/claims-v3/lib.sh` sets it from `V3_DEVICE=<n>`. `/opt/et/bin/dev_mngt_service` is the stock build:
it ignores `ET_DEVICES` and opens every card, so pass `-n <N>` to it.

**Leave the cards' configuration alone.** aifoundry3's clock guard is deliberate. Changing a TDP, a clock, the
firmware or the driver on a shared machine silently changes what other people's runs measure, in the middle of their
experiments. Those are lab-admin decisions: ask. The same goes for resets. A lab admin can reset one card through
sysfs (`/sys/bus/pci/devices/<BDF>/soc_reset/reinitiate`, root): on 25 September that brought aifoundry3's card back
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

## Traps that cost time here

- **`sparsity_host --budget` defaults to 8 seconds** on silicon and silently stops a longer run. Raise it for
  anything past 8 s.
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
  per partner. On silicon this hangs the hart permanently and the card needs a power cycle; `sys_emu` does not
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
  same runs. The fault is in a runtime helper thread (`_Rb_tree_insert_and_rebalance`), and the prime suspect is
  aifoundry3's patched `-O3` `libetrt.so` (the host table above); replacing it with the stock build has not been
  done. Treat such a launch as failed and repeat it, and do not read it as a workload bug. Cores are kept now:
  `coredumpctl list`, `coredumpctl gdb <pid>`.
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
- [03-experiments.md](03-experiments.md): the standard protocol and every session's command.
