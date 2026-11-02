# Q134(a): aifoundry2's over-power alarm, read from the POWER_SAFE residency counter

*This answers item 14, "aifoundry2's alarm", in the kinds page's [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open).
It is a desk lane, Sun 1 Nov 2026 (PST), and every result in it is post hoc: nothing was pre-registered. It builds on
[Q132(g)](../2026-11-01-q132-governor-desk/README.md) §a, which narrowed item 14, and on [E77](../2026-11-01-e77-rail-one-temperature/README.md)'s
lead: raw throttle-residency state 3 (POWER_SAFE) read 0 at all 11 of E77's reads. The positive control is
[E84](../2026-10-31-e84-speed-aifoundry1-card0/README.md)'s card 0. There was no card session. Two read-only host reads,
at 19:14:57 and 19:15:19 PST, opened no device node and took no lock.*

## Results first

1. **aifoundry2's service processor has not been in POWER_SAFE once since it started on 26 Oct 2026.**
   - **The reads.** Raw state 3 read **0 µs at all 712 committed reads**, from 11 sessions, E69 (27 Oct 14:20:45 PDT)
     through E77 (1 Nov 17:59:25 PST).
   - **The counter was live and never cleared.** Over the same reads, raw state 2 (POWER_DOWN) rose monotonically from
     1,095.9 s to 4,717.6 s.
   - **One lifetime covers every read.** E77's module uptime, 6 d 3 h 46 m at 17:59:25 PST, puts the start between
     15:12:25 and 15:13:25 PDT on 26 Oct. The host booted at 15:13:03 PDT and has not rebooted since.
   - Sources: [`reads.csv`](reads.csv), [`continuity.txt`](continuity.txt).
2. **On aifoundry1 card 0, the same counter is an exact record of the PMIC over-power alarm.** This is the positive
   control. Card 0 reports the same service-processor build, BL2 0.22.0, with PMIC 1.6.1 (E84 A1).
   - **The replay.** Card 0's kernel log holds 146 THROTTLE_TIME events, one sent as each POWER_SAFE episode ends.
     Their durations, replayed through the public source's bookkeeping (cumulative, running average, max, min),
     reproduce **all 63 committed raw-3 reads on all four fields** (E84 and E114).
   - **Only the alarm runs.** Raw 3 grew in the four fp32 random-data runs, by 3, 5, 68 and 70 episodes (1.06, 1.58,
     28.43 and 28.94 s), and in none of E84's other 31 runs or E114's runs.
   - **Each episode began with an interrupt.** Card 0 logged 177 PMIC over-power interrupts (alarm values
     75.00-76.75 W). Each of the 146 episodes began with one: 117 had one interrupt, 27 had two, 2 had three, and
     none had none.
   - **Timing.** Episodes lasted 0.284-0.462 s, mean 0.411 s. Each episode's end reached the host its own duration
     after its first interrupt, to a median of 43 µs.
   - **Time in the safe state.** In the two sustained fp32 random-data runs card 0 spent 36-37% of the time in
     POWER_SAFE, and 17-25% in the two bursts. That is 4-7 points above the share of E84's 10 Hz samples at 300 MHz
     (31-32% and 12.5-17.5%, E84 [`posthoc/pmic.txt`](../2026-10-31-e84-speed-aifoundry1-card0/posthoc/pmic.txt)).
   - Source: [`replay-card0.txt`](replay-card0.txt).
3. **The driver's two counts agree, and its event path from aifoundry2 is live.**
   - **The counts.** The driver counts each PMIC event the service processor pushes (`PmicCeEvent`) and each POWER_SAFE
     episode's end (`ThermThrottleCeEvent`). They read **0 and 0 on aifoundry2** at 19:14:57 PST, against **177 and
     146 on card 0**.
   - **The path is live.** The same driver delivered aifoundry2's 4,234 SP Runtime Error events. 4,228 of them are two
     per committed read of an invalid residency state (4-6), E77's F1 mechanism, and on card 0 that rule gives all
     378.
   - Source: [`counters.txt`](counters.txt).
4. **How far these zeros reach on aifoundry2.** Thirteen sessions have run there since its start. Their telemetry
   holds:
   - 415,502 readings: 5,406 at 75 W or more, 2,687 at 80 W or more, 965 at 85 W or more, and 3 at 100 W or more;
   - 624 readings at 86.23 W or more, which is card 0's 75 W on aifoundry2's reading by Q132(g)'s line
     a2 = 2.46 + 1.117 c0;
   - a highest reading of **101.15 W** (E101, `SUS-19-mm16-fp16-randn`);
   - 94 runs that passed 80 W;
   - no reading at 300 MHz.

   The PMIC's own average, `sp.board_avg_w`, peaked at **71.85 W** and never reached 75 W.
   Sources: [`sessions.json`](sessions.json), [`runs-80w.txt`](runs-80w.txt).

## What this settles for item 14, and what it does not

**Settled: aifoundry2 has never had card 0's alarm.**
- **The interrupt never came.** On card 0 the alarm is a PMIC over-power interrupt, which the service processor's
  handler maps to POWER_SAFE (300 MHz, about 0.4 s). That interrupt has never reached aifoundry2's service processor
  in its six-day life. Its readings went up to 101.15 W, about 88 W on card 0's scale. A PMIC over-temperature
  interrupt maps to the same state, so none of those came either.
- **The new wording.** Item 14 said "no alarm at any reading it reports, up to 88.88 W". It can now say "no over-power
  interrupt at all since the 26 Oct start, up to 101.15 W".
- **Why this record is stronger.** The ring can overwrite what it held: Q132(g) found rings reaching back for only 23
  of 93 runs at 75 W or more. Sampling can miss an episode. This counter does neither.
- **No power cycle either.** The public source lists an over-power power cycle among the PMIC's reset causes
  (`pmic_hal.h:62`). The service processor has not restarted since 26 Oct, so no such cycle happened at these powers.

**Not settled:**
1. **An alarm on the slow average.** Suppose aifoundry2's PMIC compares its average, or any filtered quantity, with its
   75 W set point. Then it never had a chance to fire: the governor's 65 W TDP held the average at or below 71.85 W.
   The counters cannot tell "no alarm" from "an alarm on a quantity that never crossed", so item 14's "slow average
   untested" stands. Settling it needs one of two things:
   - a governor move that lets the average pass 75 W, which is E117's design (not run, awaiting the owner's acceptance
     of a possible outage);
   - a PMIC read of the alarm's configuration, which is a PMIC command.
2. **Whether the PMIC raises its line, and so firmware or board.** All three counts sit downstream of the service
   processor's PMIC interrupt handler, which calls the POWER_SAFE callback and then pushes the host event
   (`pmic_controller.c:712-781`). So they show that the handler never ran: `PmicCeEvent` 0 covers every cause it
   pushes, unknown causes included. They do not show whether the PMIC raised its interrupt line. A PMIC that interrupts on a board where nothing services the line
   would read the same. Firmware (PMIC 1.5.0 here, 1.6.1 on card 0) or board: still unknown.
3. **The exact build.** No allowed query shows a BL2 hash.
   - Card 0's running BL2 0.22.0 keeps this counter exactly as `836a4ab`'s source does: 63 of 63 reads match, on four
     fields each. Its episodes also behave as the source says they enter and leave: each starts at an interrupt, a
     repeat interrupt inside an episode starts no new one, and the time is added at the episode's end.
   - aifoundry2 reports the same release 1.4.0, BL1/BL2 0.22.0 and minions 0.25.1 (E69's read), so it very likely runs
     the same image. No hash proves it.
4. **aifoundry2's set point.** At boot the service processor writes 75 W (`main.c:552` → `pmic_set_tdp_threshold`,
   `pmic_controller.c:503-516`). Whether that write took effect on aifoundry2 has not been read, and reading it would
   be a PMIC read.

## How POWER_SAFE is counted (et-platform `836a4ab`, the source for BL2 0.22.0)

Paths are relative to `device-bootloaders/src/ServiceProcessorBL2/` unless they say otherwise.

- **States.** `device-api/include/management-api/device_mgmt_api_spec.h:280-286`: IDLE 0, UP 1, DOWN 2, SAFE 3,
  UNKNOWN 4. This is why reading raw 4 fails with rc -5 and logs SP errors.
- **The only way in.** The one POWER_SAFE notification is in `pmic_isr_callback` (`services/thermal_pwr_mgmt.c:2317-2323`),
  on an OV_TEMP or OV_POWER cause bit. It is registered at `:1686`. The PMIC error handler calls it in both its
  over-temperature and over-power branches, before pushing the host event (`driver/pmic_controller.c:724-781`). An
  unknown cause pushes an event too (`:712-721`). Every other notifier sets a different state: DOWN at `:894` and
  `:907`, UP at `:919`, IDLE at `:3119`.
- **Leaving, and when the time is added.** POWER_SAFE is always allowed, and DOWN is ignored while in it (`:2244-2266`).
  Time is added only when the state changes (`:2146-2161`, `:2097-2144`). So an episode is counted once an UP or IDLE
  event ends it, and at that moment a THROTTLE_TIME event goes to the host (`:2112-2129`, the only sender).
- **The arithmetic.** `update_residency` (`:351-393`): cumulative `+=`, average `(average + t) / 2`, maximum, minimum.
- **The read.** `DM_CMD_GET_MODULE_RESIDENCY_THROTTLE_STATES` (29) goes to `services/thermal_power_monitor.c:596-623`,
  which calls `get_throttle_residency` (`thermal_pwr_mgmt.c:1477-1505`). It is a copy from service-processor RAM and
  touches no PMIC.
- **Nothing clears it but a restart.**
  - `g_soc_power_reg` lives in `.data` (`:143`), and only `update_residency` writes its four throttle structs.
  - The statistics reset, allowed by the owner's ruling of 31 October 2026, goes through `services/performance.c:546-612`
    to `Thermal_Pwr_Mgmt_Init_OP_Stats` (`thermal_pwr_mgmt.c:2805`). That function resets `op_stats`, the PVT hi/lo and
    the PMB stats, and leaves the residency alone.
  - The data agree. Raw 2 read 2,251,185,337 µs at E83's last read (31 Oct 15:07:37 PDT) and again at E87's first
    (19:49:01 PDT). E85's 2,205 statistics resets ran between them.
- **What the module uptime counts.** It is "the cumulative time starting from Device Reset" (`thermal_pwr_mgmt.c:1430-1455`).
- **The driver.** It counts THROTTLE_TIME as "Thermal Throttling Error" in `ThermThrottleCeEvent`, and PMIC events in
  `PmicCeEvent` (`et-driver/et_event_handler.c:664-688`). The two message-ID enums align (`et-driver/et_device_api.h:64-81`
  against `include/dm_event_def.h:38-58`). The syndrome prints each duration with the unit "msec", but the service
  processor sends microseconds, as the exact replay shows.

## Side findings, for the records

- **The SP Runtime Error events on these cards are the lab's own residency reads.** A read of an invalid state (4, 5
  or 6) raises two events, E77's F1 mechanism.
  - **Card 0.** It held 252 events at Q132(g)'s 00:13 PDT count, which is 126 invalid-state reads × 2 (E84). It holds
    378 now, which is 189 × 2.
  - **E114's open events.** The 126 events added between 00:13 PDT and E118's 14:50:39 PST count are E114's 21
    committed reads × 3 invalid states × 2. Those reads are 17 in s1 and 4 in the smoke; the records' "51 reads of
    states 4-6" counts s1 only (17 × 3). So the 120 events that `docs/findings/14-card-behaviour.md` places in E114's
    session and leaves open are E114's own residency reads, not the stock sampler's voltage-register reads or that
    session's load.
  - **aifoundry2.** It held 1,692 events at 00:13 PDT and holds 4,234 now, against 2 × 843 and 2 × 2,114 committed
    invalid-state reads. Six events, three invalid-state reads, are in no committed file, all from before 00:13 PDT on
    1 Nov.
  - **The fix.** Every session here but E77 read states 2-6: 701 of aifoundry2's 712 reads and all 63 of card 0's.
    E77's amendment A1 read states 2-4. Reading states 2 and 3 only would stop the events.
- **The unit in the log.** The kernel log's "Thermal Throttling Duration Beyond Threshold: N msec" is N microseconds.

## What it changes

- **Kinds page section 11 item 14, the Horace hub's Status and Levels stop 1** (integration lanes only):
  - from "aifoundry2 shows no alarm at any reading it reports, up to 88.88 W, on a reading not shown to be card 0's
    quantity";
  - to "aifoundry2's service processor has never taken a PMIC over-power interrupt since it started on 26 Oct:
    POWER_SAFE read 0 at 712 reads, and the driver counts 0 PMIC events and 0 throttle-time events, at readings up to
    101.15 W (card 0, on the same service-processor build, counts 146 episodes and 60.0 s exactly). An alarm on the
    slow average, which peaked at 71.85 W, and firmware or board stay open".
- **For the blog.** Card 0's third limit, the PMIC alarm, is absent on aifoundry2 at its fast reading. There, the power
  cap and the thermal threshold are the only limits seen.

## Departures and method

- **Nothing registered.** This desk lane is post hoc throughout.
- **One departure from the brief's letter.** The brief named committed data plus one optional residency read on
  aifoundry2. This lane also read each host's driver counters and the kernel log's ET events
  ([`host/host_read.sh`](host/host_read.sh)). That is a host read like `et-who`: it opens no device node and takes no
  lock. The committed copies leave out the login counts.
- **The optional residency read was not made.** Since E77's last read (17:59:25 PST), the only use of aifoundry2 had
  been the E77 verifier's one config read at 18:30:53 PST, so a fresh read could add no high-power test. The host
  counters already reach 19:14:57 PST without opening the card. And E119 was preparing to take aifoundry2.
- **What [`q134a_residency.py`](q134a_residency.py) does.** It finds every residency list in the 13 data dirs (11
  sessions on aifoundry2, plus E84 and E114 on card 0), drops the runners' duplicate copies (`runs.jsonl` repeats
  `queries.jsonl`), and writes one row per read. It tallies `board_w` and `sp.board_avg_w` over the telemetry of the
  13 aifoundry2 sessions since the start (E73's and E85's camera sessions read no residency). It replays card 0's
  kernel-log durations, and checks the event counts and the uptime.
- **To re-run it:** `python3 docs/reports/data/2026-11-01-q134a-alarm-residency/q134a_residency.py` from the top of
  the repository, about a minute.

## Files

- [`results.json`](results.json): the headline numbers.
- [`reads.csv`](reads.csv): every residency read, one row each (775).
- [`sessions.json`](sessions.json): aifoundry2's sessions, with their power maxima and residency spans.
- [`runs-80w.txt`](runs-80w.txt): the 94 runs that passed 80 W.
- [`replay-card0.txt`](replay-card0.txt) and [`replay-card0.json`](replay-card0.json): the positive control.
- [`counters.txt`](counters.txt): the driver's counts and the SP-error accounting.
- [`continuity.txt`](continuity.txt): uptime, boot times and monotonicity.
- [`host/`](host/): the two host reads and their script.
