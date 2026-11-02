# Q134(a): aifoundry2's over-power alarm, read from the POWER_SAFE residency counter

*This answers item 14, "aifoundry2's alarm", in the kinds page's [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open).
It is a desk lane, Sun 1 Nov 2026 (PST), and every result in it is post hoc: nothing was pre-registered. It builds on
[Q132(g)](../2026-11-01-q132-governor-desk/README.md) §a, which narrowed item 14 and found the driver's PMIC event
counter at 0 on aifoundry2 since its 26 Oct boot, and on [E77](../2026-11-01-e77-rail-one-temperature/README.md)'s
lead: raw throttle-residency state 3 (POWER_SAFE) read 0 at all 11 of E77's reads. The positive control is
[E84](../2026-10-31-e84-speed-aifoundry1-card0/README.md)'s card 0. There was no card session. Two read-only host reads,
at 19:14:57 and 19:15:19 PST, opened no device node and took no lock.*

> **Corrected at the desk, Sun 1 Nov 2026, about 20:10 PST**, after an independent verification returned
> *holds-with-fixes* on eleven minor faults. No card was touched and nothing was re-measured. The residency reads, the
> card-0 replay and the driver counts did not change. The telemetry tally did: it now counts each sample once and covers
> every aifoundry2 session since the start. That moved its totals (456,199 readings from 15 sessions, not 415,502 from
> 13) but not its maxima (101.15 W; the slow average 71.85 W). Every change is listed under
> [Corrections after verification](#corrections-after-verification).

## Results first

1. **aifoundry2's service processor has not been in POWER_SAFE once since it started on 26 Oct 2026.**
   - **The reads.** Raw state 3 read **0 µs at all 712 committed reads**, from 11 sessions, E69 (27 Oct 14:20:45 PDT)
     through E77 (1 Nov 17:59:25 PST).
   - **The counter was live and never cleared.** Over the same reads, raw state 2 (POWER_DOWN) rose monotonically from
     1,095.9 s to 4,717.6 s.
   - **One lifetime covers every read.** E77's module uptime, 6 d 3 h 46 m at 17:59:25 PST, puts the start between
     15:12:25 and 15:13:25 PDT on 26 Oct. The host booted at 15:13:03 PDT and has not rebooted since.
   - **Only this lifetime.** Nothing here reaches back before 26 Oct, and raw-state numbers depend on the build. In
     September aifoundry2 ran BL2 0.20.0, where POWER_SAFE was raw state 5, not 3; 0.18.0 numbers the states as 0.20.0
     does ([DVFS2 design](../2026-09-28-dvfs2-aifoundry2/plan/DESIGN.md), lines 419 and 709). There raw 5 read 0 at all
     21 reads, and raw 3, another state, read 606,112 µs
     ([`raw/p*/z1.json`](../2026-09-28-dvfs2-aifoundry2/raw/)). The design records that the alarm had not fired, even
     at 87.8 W.
   - Sources: [`reads.csv`](reads.csv), [`continuity.txt`](continuity.txt).
2. **On aifoundry1 card 0, the same counter is an exact record of the PMIC over-power alarm.** This is the positive
   control. Card 0 reports the same release as aifoundry2, BL2 0.22.0, with PMIC 1.6.1 (E84 A1; aifoundry2 reports
   PMIC 1.5.0, E69). No allowed query shows a hash, so the two images are not proven to be one (Not settled 3).
   - **The replay.** Card 0's kernel log holds 146 THROTTLE_TIME events, one sent as each POWER_SAFE episode ends.
     Their durations, replayed through the bookkeeping of a public tree that declares 0.22.0 (et-platform `836a4ab`:
     cumulative, running average, max, min), reproduce **all 63 committed raw-3 reads on all four fields** (E84 and
     E114).
   - **Only the alarm runs.** Raw 3 grew in the four fp32 random-data runs, by 3, 5, 68 and 70 episodes (1.06, 1.58,
     28.43 and 28.94 s), and in none of E84's other 31 runs or E114's runs.
   - **177 alarms, 146 episodes.** Card 0's PMIC raised 177 over-power interrupts (alarm values 75.00-76.75 W). They
     made 146 episodes, each begun by an interrupt: 117 had one interrupt, 27 had two, 2 had three, and none had none.
     A repeat interrupt inside an episode starts no new one.
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
   - **What is new here.** The `PmicCeEvent` zero since the 26 Oct boot is Q132(g)'s finding, read at 00:13 PDT on
     1 Nov. This lane adds three things: the service processor's own POWER_SAFE counter, with its exact control on
     card 0; the throttle-time count, which the replay ties to that counter episode by episode; and the reach to
     19:14:57 PST, past E96, E98, E100, E101, E105, E111 and E77, where the highest readings are.
   - **The path is live.** The same driver delivered aifoundry2's 4,234 SP Runtime Error events. 4,228 of them are two
     per committed read of an invalid residency state (4-6), E77's F1 mechanism, and on card 0 that rule gives all
     378.
   - Source: [`counters.txt`](counters.txt).
4. **How far these zeros reach on aifoundry2.** At least 16 card sessions ran there between its start and the 19:14:57
   PST host read: E66, E68, E69, E72, E73, E77, E80, E83, E85, E87, E96, E98, E100, E101, E105 and E111. E119 took the
   card after that read. All but E66, an idle run, have committed `board_w` telemetry. Counting each sample once, it
   holds:
   - **456,199 readings**: 6,158 at 75 W or more, 3,438 at 80 W or more, 1,045 at 85 W or more, and 3 at 100 W or more;
   - 1,620 readings at 84 W or more and 624 at 86.23 W or more. Q132(g) puts card 0's 75 W at about 84-86 W on
     aifoundry2's reading, and 86.23 W is its line a2 = 2.46 + 1.117 c0 at 75 W;
   - a highest reading of **101.15 W** (E101, `SUS-19-mm16-fp16-randn`);
   - 137 runs that passed 80 W, 43 of them E68's;
   - no reading at 300 MHz.

   The PMIC's own average, `sp.board_avg_w`, peaked at **71.85 W** (E101) and never reached 75 W. The highest reading
   in each format (fp16 101.15 W, fp32 96.25 W, int8 90.07 W) comes from E101 or E105, at the card's TDP of 65 W and
   threshold of 65 °C. The sessions also include E69's caps of 35-55 W and thresholds of 62 and 70 °C, and windows at
   TDP 0 in E72 and E77.
   Sources: [`sessions.json`](sessions.json), [`runs-80w.txt`](runs-80w.txt), [`results.json`](results.json)
   `aifoundry2.telemetry`.

## What this settles for item 14, and what it does not

**Settled: since its 26 Oct start, aifoundry2 has not had card 0's alarm.**
- **The interrupt never came.** On card 0 the alarm is a PMIC over-power interrupt, which the service processor's
  handler maps to POWER_SAFE (300 MHz, about 0.4 s). No such interrupt has reached aifoundry2's service processor in
  its six-day life. Its readings went up to 101.15 W, about 88 W on card 0's scale if Q132(g)'s line holds there. A
  PMIC over-temperature interrupt maps to the same state, so none of those came either.
- **The new wording.** Item 14 reads "From untested to no alarm at any reading it reports, on a reading not shown to be
  card 0's quantity". It can now say "no over-power interrupt at all since the 26 Oct start, at readings up to
  101.15 W". The readings are still not shown to be card 0's quantity. The counters do not depend on the reading.
- **Why this record is stronger.** The ring can overwrite what it held: Q132(g) found rings reaching back for only 23
  of 93 runs at 75 W or more. Sampling can miss an episode. Q132(g)'s `PmicCeEvent` zero already closed both gaps from
  the host's side. The residency counter closes them inside the service processor, with an exact control on card 0,
  and the throttle-time count agrees.
- **No power cycle either.** The public source lists an over-power power cycle among the PMIC's reset causes
  (`include/pmic_hal.h:62`). The service processor has not restarted since 26 Oct, so no such cycle happened at these
  powers.

**Not settled:**
1. **An alarm on the slow average, or on any filtered quantity.** Suppose aifoundry2's PMIC compares its average, or
   any filtered quantity, with its 75 W set point. Then it never had a chance to fire: the governor's 65 W TDP held the
   average at or below 71.85 W. The counters cannot tell "no alarm" from "an alarm on a quantity that never crossed", so
   item 14's "slow average untested" stands. Settling it needs one of two things:
   - a governor move that lets the average pass 75 W, which is E117's design (not run, awaiting the owner's acceptance
     of a possible outage);
   - a PMIC read of the alarm's configuration, which is a PMIC command.
2. **Whether the PMIC raises its line, and so firmware or board.** All three counts sit downstream of the service
   processor's PMIC interrupt handler, which calls the POWER_SAFE callback and then pushes the host event
   (`driver/pmic_controller.c:712-781`). So they show that the handler never ran: `PmicCeEvent` 0 covers every cause it
   pushes, unknown causes included. They do not show whether the PMIC raised its interrupt line. A PMIC that interrupts
   on a board where nothing services the line would read the same. Firmware (PMIC 1.5.0 here, 1.6.1 on card 0) or
   board: still unknown.
3. **The exact build.** No allowed query shows a BL2 hash.
   - Card 0's running BL2, reported as 0.22.0, keeps this counter exactly as the public tree `836a4ab` does: 63 of 63
     reads match, on four fields each. Its episodes also behave as that source says they enter and leave: each starts at an interrupt,
     a repeat interrupt inside an episode starts no new one, and the time is added at the episode's end.
   - `836a4ab` declares version 0.22.0 (`device-bootloaders/CMakeLists.txt:4`). Nothing shows that either card's image
     was built from it.
   - aifoundry2 reports the same release 1.4.0, BL1/BL2 0.22.0 and minions 0.25.1 (E69's read), so it very likely runs
     the same image as card 0. No hash proves it.
4. **aifoundry2's set point.** At boot the service processor writes 75 W: `common/main.c:552` calls
   `enable_pmic_interrupts` (`driver/pmic_controller.c:503-516`), which calls
   `pmic_set_tdp_threshold(POWER_THRESHOLD_HW_CATASTROPHIC)`, 75 in `include/bl2_pmic_controller.h:262`. Whether that
   write took effect on aifoundry2 has not been read, and reading it would be a PMIC read.

## How POWER_SAFE is counted (et-platform `836a4ab`, a public tree that declares BL2 0.22.0)

Paths are relative to `device-bootloaders/src/ServiceProcessorBL2/`, except those starting `device-api/`,
`device-bootloaders/` or `et-driver/`, which start at the top of the et-platform tree.

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
  which calls `get_throttle_residency` (`services/thermal_pwr_mgmt.c:1477-1505`). It is a copy from service-processor
  RAM and touches no PMIC.
- **Nothing clears it but a restart.**
  - `g_soc_power_reg` lives in `.data` (`:143`), and only `update_residency` writes its four throttle structs.
  - The statistics reset, allowed by the owner's ruling of 31 October 2026, goes through `services/performance.c:546-612`
    to `Thermal_Pwr_Mgmt_Init_OP_Stats` (`services/thermal_pwr_mgmt.c:2805`). That function resets `op_stats`, the PVT
    hi/lo and the PMB stats, and leaves the residency alone.
  - The data agree. Raw 2 read 2,251,185,337 µs at E83's last read (31 Oct 15:07:37 PDT) and again at E87's first
    (19:49:01 PDT). E85's 2,205 statistics resets ran between them.
- **What the module uptime counts.** It is "the cumulative time starting from Device Reset"
  (`services/thermal_pwr_mgmt.c:1430-1455`).
- **The driver.** It counts THROTTLE_TIME as "Thermal Throttling Error" in `ThermThrottleCeEvent`, and PMIC events in
  `PmicCeEvent` (`et-driver/et_event_handler.c:664-688`). The two message-ID enums align (`et-driver/et_device_api.h:64-81`
  against `include/dm_event_def.h:38-58`).
- **The unit.** The syndrome prints each duration with the unit "msec", but the number is microseconds. The host's
  clock shows it. Read as microseconds, each episode's end reaches the host its own duration after its first
  interrupt, to a median of 43 µs (range -35 µs to 13.9 ms). Read as milliseconds, every episode would end 283-461 s
  before its own first interrupt ([`replay-card0.txt`](replay-card0.txt)). The exact replay shows only that the logged
  number equals the counter's.

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
- **The unit in the log.** The kernel log's "Thermal Throttling Duration Beyond Threshold: N msec" is N microseconds,
  by the host-clock test above.

## What it changes

- **Kinds page section 11 item 14 and the Horace hub's Status** (integration lanes only). Item 14 reads "From untested
  to no alarm at any reading it reports, on a reading not shown to be card 0's quantity". It can say:
  "aifoundry2's service processor has not taken a PMIC over-power interrupt since it started on 26 Oct. POWER_SAFE read
  0 at 712 reads, and the driver counts 0 PMIC events (Q132(g)'s zero, carried to 1 Nov 19:14:57 PST) and 0
  throttle-time events, at readings up to 101.15 W (about 88 W on card 0's scale if Q132(g)'s line holds there). Card
  0, on the same reported release, counts 146 episodes and 60.0 s exactly. Open: an alarm on the slow average or any
  filtered quantity (the average peaked at 71.85 W), whether aifoundry2's PMIC raises its line (firmware or board), and
  the set point."
- **The Horace hub's Levels stop 1** (integration lanes only). Replace the whole clause "aifoundry2 shows no alarm at
  any reading it reports, up to 88.88 W, on a reading not shown to be card 0's quantity (it reads 5–10 W above card 0
  at the same kind and clock), firmware or board unknown" with "aifoundry2's service processor has not entered
  POWER_SAFE since its 26 Oct start, at readings up to 101.15 W (it reads 5–10 W above card 0 at the same kind and
  clock): its POWER_SAFE counter read 0 at 712 reads, and the driver counts no PMIC or throttle-time event (Q134(a));
  an alarm on the slow average or any filtered quantity, and firmware or board, stay open". The stop's open column,
  "why aifoundry2 shows no alarm, firmware or board, and the slow average, untested (either a governor move or a PMIC
  read)", still holds.
- **For the blog.** Card 0's third limit, the PMIC alarm, has been absent on aifoundry2 since 26 Oct at its fast
  reading. There, the power cap and the thermal threshold are the only limits seen.

## Departures and method

- **Nothing registered.** This desk lane is post hoc throughout.
- **One departure from the brief's letter.** The brief named committed data plus one optional residency read on
  aifoundry2. This lane also read each host's driver counters and the kernel log's ET events
  ([`host/host_read.sh`](host/host_read.sh)). That is a host read like `et-who`: it opens no device node and takes no
  lock. The committed copies leave out the login counts.
- **The optional residency read was not made.** Since E77's last read (17:59:25 PST), the only use of aifoundry2 had
  been the E77 verifier's one config read at 18:30:53 PST, so a fresh read could add no high-power test. The host
  counters already reach 19:14:57 PST without opening the card. And E119 was preparing to take aifoundry2.
- **What [`q134a_residency.py`](q134a_residency.py) does.**
  - **Residency.** It finds every residency list in the 13 data dirs that hold residency reads (11 sessions on
    aifoundry2, plus E84 and E114 on card 0) and writes one row per read. No residency list appears in two files: the
    guard that would drop a copied read drops none (`results.json`, `aifoundry2.residency_duplicate_rows_dropped` = 0).
  - **Telemetry.** It tallies `board_w` and `sp.board_avg_w` over the 16 aifoundry2 card sessions with committed data
    since the start (E68, E72, E73 and E85 read no residency; E66 has no telemetry). It counts each sample once, by
    its time and reading (`t_ms`, `board_w`). E111's `CAM-RED/tel.jsonl.gz` is a byte-for-byte copy of
    `CAM/tel.jsonl.gz` (12,122 samples) and `CAM/tel.jsonl.raw` an earlier partial dump (393), so 12,515 repeated lines
    are dropped. The 728 per-launch summary lines (E73 248, E85 240, E111 240) carry a `board_w` but no `t_ms`, and
    reach 31.75 W at most. They are not samples and are left out.
  - **The rest.** It replays card 0's kernel-log durations, and checks the event counts and the uptime.
- **To re-run it:** `python3 docs/reports/data/2026-11-01-q134a-alarm-residency/q134a_residency.py` from the top of
  the repository, about a minute.

## Files

- [`results.json`](results.json): the headline numbers.
- [`reads.csv`](reads.csv): every residency read, one row each (775).
- [`sessions.json`](sessions.json): aifoundry2's 16 sessions, with their power maxima, residency spans, and the
  repeated and summary lines left out of the tally.
- [`runs-80w.txt`](runs-80w.txt): the 137 runs that passed 80 W.
- [`replay-card0.txt`](replay-card0.txt) and [`replay-card0.json`](replay-card0.json): the positive control, and the
  host-clock test of the unit.
- [`counters.txt`](counters.txt): the driver's counts and the SP-error accounting.
- [`continuity.txt`](continuity.txt): uptime, boot times and monotonicity.
- [`host/`](host/): the two host reads and their script.

## Corrections after verification

Sun 1 Nov 2026, about 20:10 PST, at the desk, after an independent verification returned *holds-with-fixes* on eleven
minor faults. No card was touched and nothing was re-measured. `reads.csv`, `counters.txt` and `continuity.txt` are
unchanged, and so are the replay's numbers.

1. **The telemetry total.** "415,502 readings" counted E111's camera telemetry two or three times and counted 728
   per-launch summary lines as readings. `CAM-RED/` repeats `CAM/`, and `CAM/tel.jsonl.raw` repeats part of it. With
   each sample counted once, the same 13 sessions hold 402,259 readings, and no threshold count or maximum changes.
2. **The sessions.** "Thirteen sessions have run there since its start" was false: E66, E68 and E72 ran on aifoundry2
   in this lifetime too. The verification took all three to have no `board_w` telemetry. E66, an idle run, has none,
   but E68 (26 Oct, 21:10-22:30 PDT) and E72 (27 Oct, 15:01-15:24 PDT) have 10 Hz telemetry in their
   `telemetry.jsonl.gz` files: 41,264 and 12,676 readings. They are now in the tally. E68 reached 85.96 W and E72
   59.67 W.
   - **What moved:** 456,199 readings; 6,158 at 75 W or more (was 5,406); 3,438 at 80 W or more (was 2,687); 1,045 at
     85 W or more (was 965); 137 runs past 80 W (was 94).
   - **What did not:** 624 at 86.23 W or more, 3 at 100 W or more, the 101.15 W maximum, the 71.85 W average maximum,
     and no reading at 300 MHz.
   - **Conditions.** Each format's highest reading is E101's or E105's, at TDP 65 W / 65 °C. The lane's table cells
     said "TDP 65 W / 65 C, 26 Oct-1 Nov", which was too broad: E69 also ran caps of 35-55 W and thresholds of 62 and
     70 °C, and E72 and E77 had windows at TDP 0.
3. **The method line** said the script dropped duplicate residency copies (`runs.jsonl` repeating `queries.jsonl`).
   There are none. The de-duplication that matters is the telemetry's (1).
4. **The build.** "The same service-processor build" and "`836a4ab`, the source for BL2 0.22.0" are now "the same
   reported release" and "a public tree that declares 0.22.0". No hash proves that either card runs it.
5. **"Never" and "ever"** are scoped to the lifetime that began on 26 Oct. Results 1 now warns that raw-state numbers
   differ between BL2 0.18.0/0.20.0 (POWER_SAFE = 5) and 0.22.0 (POWER_SAFE = 3).
6. **Item 14's wording** is now quoted as item 14 has it. "Up to 88.88 W" is Levels stop 1's wording, and What it
   changes now gives stop 1's whole clause.
7. **Two caveats restored** in the suggested wording: "about 88 W on card 0's scale if Q132(g)'s line holds there",
   and "the slow average or any filtered quantity". Results 4 adds the count at 84 W, the low end of Q132(g)'s 84-86 W.
8. **Credit.** The driver's `PmicCeEvent` zero since the 26 Oct boot is Q132(g)'s. What this lane adds is now stated:
   the residency counter with its exact control on card 0, the throttle-time count, and the reach to 19:14:57 PST.
9. **The unit.** The microsecond reading is shown by the host-clock lag, not by the replay. `replay-card0.txt` now
   prints the lag both ways.
10. **A path.** `main.c:552` is `common/main.c:552`, and the chain to the 75 W write is spelled out. `pmic_hal.h` and
    `pmic_controller.c` now carry their directories too.
11. **Alarms and episodes.** Results 2 now says the 177 alarms made 146 episodes. The lane's blog lines, outside this
    file, had confused the two.
