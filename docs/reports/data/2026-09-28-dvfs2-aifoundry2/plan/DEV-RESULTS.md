# DV2 development results: aifoundry2, night of 27-28 Sep 2026 (PDT)

Written 28 Sep, about 03:10 PDT, after the development queue stopped. Everything here is **development data**: it
chose parameters and rules, it tests nothing. The frozen test is `PREREG-VAL.md` (this directory).

**Sources.**
- The raw data: `/home/yaroslavvb/claude/et-soc1-dvfs2/build/claims-v3/aifoundry2/dv2/`, copied to `dev/dv2/` here,
  with the queue log (`dev/queue-dv2-aifoundry2.log`) and the decision log (`dev/dv2/dev-log.jsonl`).
- The reductions:
  - `dev/dv2-dev.json` (`reduce_dv2.py --dev`);
  - `dev/dev-idle.json` (`dv2v/reduce_val.py --dev`: the idle items and the NAT items on development data);
  - `dev/z1ev.json` (`z1ev.py`: every governor line of the night).
- aifoundry3: `~/nekko/build/claims-v3/aifoundry3/dv2/z2-20260928T003343/z2.json`.

---

## 1. What ran

| Time (PDT) | Card | Pass | What | Card time |
|---|---|---|---|---|
| 00:33 | aifoundry3 | Z2 (`dv2/z2.sh`) | read-only: uptime, residency 2-6, config, ring | about 1 s |
| 00:40-02:54 | aifoundry2 | Z1 p1001-p1012, p1101-p1112 | 21 read-only watch cycles (10 min apart, then 2 min from 02:32) | about 1.5 s each |
| 01:30-01:38 | aifoundry2 | NAT p6035 | NAT-1 (R0 64): probe, smoke, ADD, one T-block; ended early (DEVIATION-N3) | 7.5 min |
| 02:00-02:25 | aifoundry2 | NAT p6038 | NAT-4 (R0 60): probe, smoke, ADD, 3 T-blocks, 2 RST runs, ADD | 25 min |
| 02:30 | aifoundry2 | smoke p4001 | one 2 s UNI32@4 launch | 18 s |
| 02:31 | aifoundry2 | C1m p5001 | **skipped by its rule**: a Z1 reading ≤ 64 within 60 min (the card was cool) | 0 |
| 02:50-02:51 | aifoundry2 | NAT p6041 | continuation NAT-4 (R0 59): probe, smoke, then the **Master Minion hung** at the second lift of its ADD run | 53 s |

- The queue was stopped at 02:54 (`build/claims-v3/STOP`, `dv2/NIGHT-STOP`, `dv2/ALERT-MM-HANG.json`).
- No threshold, TDP, clock or voltage was set. The SP log level was never changed (§4, DEV-5). No reset was attempted.
- The caps never tripped. The highest reading of the night was 72 °C (idle, 00:40). Every post-run clock check passed:
  600 MHz 0.00-1.15 s after the kernel end, and at 600 MHz at every tail's end.
- aifoundry1: not touched.

---

## 2. The incident: the Master Minion hung (02:50:53)

- **What happened.** In p6041, the ADD run's first lift (UNI32@4, 7 s) ran normally: 800 MHz, the device held for
  7.46 s.
  - The second lift was launched 0.6 s later, while the governor's idle reset (800 → 600 MHz) was due.
  - Its kernel never started: board power stayed at the 26 W idle and the clock at 600 MHz. The heater reported
    "kernel did not finish within 6 s, aborting the stream". `timeout 10` then stopped the process (rc 124).
  - Lifts 3 and 4 failed at runtime creation: "Couldn't use the HPSQ. Perhaps the Master Minion is hanged?"
    (rc 1). After three heater failures the session aborted.
- **The service processor is fine.** Z1 at 02:52 and 02:54 read normally: 600 MHz, 25.9 W idle, 60 °C, threshold
  65.
- **Needed:** the lab admin must restore the Master Minion. Until then no kernel can run on aifoundry2.
- **Cause.** Not established. Tonight's other 45 heater launches (probes, smokes, lifts 0.3-0.6 s apart, runs), with
  57 climbs and 26 full descents of the clock, never hung. That this launch met the 800 → 600 idle reset is a guess, not a finding.
- **For validation.** The NAT replication launches the same heater. This is a stated risk (PREREG-VAL §7), and a
  zero-heat schedule is provided.

---

## 3. Results by theory (development)

### TH1: does the throttle follow the 34-sensor mean or the hottest shire? (the owner's first question)

**Busy, at 800 MHz (p6038, NAT-4, 12 T-runs from the falling 63 → 62 edge).**
- **G1-H, the hot hold.** In all 12 of 12 T-runs the clock held 800 MHz for at least 1.0 s after the hottest
  shire read ≥ 67 °C (thr + 2).
  - Maximum: 69 °C (thr + 4) in the B4C@32 runs (4 central shires). In block 2's B4C@32 run the high reached 67 °C
    0.5 s after the climb, and the clock stayed at 800 MHz for another 5.0 s, until the mean reached 66.
  - Under "the hottest shire", the step would have come within about 0.6 s of the high passing 65.
- **G1-T, timing.**
  - 5 separating runs over 2 blocks (the high reached 66 at 800 MHz ≥ 1.5 s before the mean did).
  - 4 of the 5 stepped down 0.1-0.2 s after the host mean first read 66.
  - None stepped within [−0.3, +0.6] s of the high reaching 66; all 5 steps came 3.3-5.7 s after it.
  - One run (INT16@12, block 2) stepped 0.9 s *before* the host mean read 66, so it fits neither window. The
    retrospective's RC saw 7 such early steps in 70.
  - The frozen rule needs ≥ 6 separating runs over ≥ 3 blocks, so this is INSUFFICIENT as a count. The direction is
    all H-mean.

**Idle (the Z1 watch; a new item, I1).**
- At 01:00:00 the mean read 64 while the hottest shire read 66 in every sample of the second, including the first,
  whose window was 0.12 s. The governor stayed out of its thermal state throughout:
  - its last line was an EXIT at 00:58:03, printed 65, with a PIDLE 0.13 s later;
  - the next line was an ENTER at 01:08:11 (the host read 67 at 01:10);
  - the THERMAL_DOWN residency counter shows no hidden episode (−0.05 ms against the lines).
- Under "the hottest shire" the governor would have entered within one dm pass (about 0.13 s).
- One separating cycle in development. The rule for validation needs ≥ 5 cycles over ≥ 3 cool stretches.
- **Also seen, not scored.** In NAT-1's lift phase (rest 64-65, UNI32@4) the clock went up to 800 MHz 15 times in
  30 s, each time within one host sample of the mean reading 65. The high over the same windows read 67-68, but
  those windows were not reset, so they cannot be scored.

### TH2: the cards run the 0.20.0 governor (a 0.40 s blocking loop, a one-call climb, no busy test)

- **Host bands (all development runs; `reduce_dv2.py`).** Every one sits inside the band frozen from the
  retrospective (PREREG-DEV §1.3):

| Band | Tonight | Retrospective |
|---|---|---|
| G2-C climbs: 700 MHz in ≤ 1 sample | 57 of 57 | 85 of 85 |
| G2-C climbs: no 700 MHz sample | 33 of 57 | 50 of 85 |
| G2-D descents: 700 dwell in [0.3, 0.7] s | 26 of 26 (median 0.5 s) | 69 of 70 |

- **T6 done.** The same code run on the 8 retrospective files reproduces RA (85, 85, 50) and RB (70, 69).
- **Idle lines (Z1 dumps; SP time).**
  - Every ENTER→EXIT interval of the idle card below 60 s (16 intervals) lies within 1.4 ms of k × 0.4053 s.
    - k = 0: 10 intervals, the loop's first re-read, 1.4 ms after the ENTER.
    - k = 1: 0.4039 and 0.4052 s. k = 2: 0.8095 and 0.8109 s. k = 3: 1.2165 and 1.2166 s.
    - HEAD, stepping once per 133-160 ms pass with no loop, cannot give that grid.
  - The ENTERs come on an idle card. In 18 of the 20, the previous governor line was a PIDLE: the SP itself had just
    called the card idle, 5 ms to 16 min earlier. HEAD's thermal branch acts only while busy.
  - There are no `new OP` lines on the idle card (the 6 seen were all during our sessions).

### TH3: no hysteresis (enter at thr + 1, exit at thr)

- **Idle lines.** All 20 ENTER lines of the night printed 66 and all 20 EXIT lines printed 65. At every crossing
  the governor flickered: an ENTER and an EXIT 1.4 ms apart, repeated for up to 4 s (7 crossings, 00:13-01:53).
- **G2-U, up-steps while hunting.** 82 of 82 came from a reading ≤ 66 and 79 of 82 from ≤ 65; none came from ≥ 67.
  The band is 100%, ≥ 80% and 0.

### TH4: launch and end latency come from the heartbeat

- **G3-L, launch to the first 800 MHz.** Median 0.9 s, maximum 1.11 s over 14 launches. The band is a median in
  [0.4, 1.0] s and all ≤ 2.2 s.
- **G3-I, kernel end to 600 MHz with no episode.** 0.00-1.15 s over 9 runs. The band is [0, 1.6] s.

### TH5 and the owner's second question: does placement delay the first throttle at 800 MHz?

- **DEV-1 under NAT-4.**
  - (128, 4) failed: 4 of 4 T-runs in block 1 were censored; from 62 the mean did not reach 66 within the 7 s
    launch.
  - The candidate moved to (192, 4) (INT16@12, PER16@12, S 62) and was kept at block 3, so it is final.
- **DEV-2:** 8 s launches, since every 7 s process took ≤ 8.0 s. **DEV-3:** 2.0 s. **DEV-10:** 5 min rest.
- **Blocks under the final candidate:** 2 (p6038 blocks 2-3). The continuation session meant to add 4 (p6041)
  ended with the Master Minion hang.

| Block | t800 INT16@12 | t800 PER16@12 | L = ln(PER/INT) |
|---|---|---|---|
| 2 | 3.60 s | 5.00 s | 0.33 |
| 3 | 3.90 s | ≥ 6.95 s (censored at the kernel end) | ≥ 0.58 |

- **Development L = 0.45** (2 blocks, SD 0.18). L_P (power-adjusted) = 0.41.
  - At 192 minions and 800 MHz, perimeter placement held 800 MHz about 1.4-1.8× as long as interior placement
    before the first throttle.
- **Theory point.** L_pred = 0.28, band ± 0.10.
  - Inputs: aifoundry3's heat-only couplings, because C1m did not run (DEV-6 fallback; L600 = 0.48 and 0.34).
  - Tonight's ADD P_U = 7.37 W (7.22 and 7.52). P_x = 9.37 W.
  - Development L lies above the band. That is "TH5 not supported in development", and it is reported only (PREREG-DEV §1.4).
  - n_val = 16 (SD 0.18 misses b = 0.10 even at 16).
- **The owner's question in sign form (new, G4-S).** Is L > 0? With L ≈ 0.45 and SD ≈ 0.18, 6 blocks give a 99%
  CI of about ±0.30, so the question is decidable in 2 NAT-4 sessions.

### TH7: the idle reset follows the exit

- 19 of 19 idle EXITs were followed, as the next governor line, by a PIDLE. That was 0.119-0.131 s later in 17 cases
  (one dm pass) and 2.6 and 12.6 ms later in the other two.

### TH8: the card states

- **aifoundry3 (Z2, 00:33).** POWER_UP, POWER_DOWN, THERMAL_DOWN and POWER_SAFE residencies were all 0 after
  2 d 8 h up. That includes THERMAL_DOWN, after HP's R3 had heated it past 66 °C that evening. **The PREREG-DEV
  §1.2 prediction is MET, on a card other than the development card.** Its thermal branch never completed an episode.
- **aifoundry2.** POWER_UP = 23.05 s, which is > 0 as predicted for an SP up since before 21 Sep (uptime 9 d 5 h).
  THERMAL_DOWN = 747,342 s: 8.65 of 9.23 days in the thermal state, with a longest stay of 2.1 days.
- **The THERMAL_DOWN counter** adds a whole episode when it ends. Across the idle intervals its change equals the
  summed ENTER→EXIT durations, less 1.33 ms per episode, within 0.2 ms (3 intervals: −0.19, −0.05, −0.06 ms). The
  1.33 ms is the gap between the ENTER line and the "throttle_state: 4" line.

### The card itself

- **The rest swings.** aifoundry2's idle reading swung between 59 and 72 °C on a 10-30 min scale:

| Time | 00:40 | 00:50 | 01:00 | 01:10 | 01:20 | 01:30 | 01:50 | 02:00 | 02:30-02:54 |
|---|---|---|---|---|---|---|---|---|---|
| Reading (°C) | 72 | 70 | 64 | 67 | 69 | 64 | 66 | 60 | 59-62 |

- **Idle power follows temperature:** 25.7 W at 59 °C, 31.1 W at 72 °C, about 0.4 W per °C.
- **The host saw no change.** Its sensors were flat: ACPI 16.8 and 27.8 °C, NVMe 43-45 °C. The driver of the swing
  is not established.
- **The crossings of 65/66** (from the ring) were at 00:13:45 (warming), 00:58:03 (cooling), 01:08:11 (warming),
  01:26:36 (cooling), 01:30:27 (one flicker), 01:46:11 (warming) and 01:53:40 (cooling).

---

## 4. Decisions and every change to the design (dev-log.jsonl)

1. **DEV-1** (N, K − S): (128, 4) → (192, 4) after block 1 (censored); kept at block 3; final (192, 4).
2. **DEV-2**, launch length: 8 s. **DEV-3**, stop delay: 2.0 s. **DEV-10**, rest: 5 min.
3. **DEV-5**, the SP-line items (G1-X, G2-E/X/N, G3-Q/H, G6-B busy): **no**.
   - The level inference read WARNING_OR_LOWER on a card at INFO, because an `ettelem sptrace` dump is a BAR read and
     logs nothing. So WARNING was never set (no global change).
   - At INFO under a 10 Hz sampler the ring holds less than 1 s, so these items are not registered.
   - The idle items (§3) take their place, and they need no level change.
4. **DEV-6**, the G4 couplings: the fallback (aifoundry3's dev-r3), labelled; C1m did not run.
5. **DEV-7**, n_val: 16. **DEV-11**, the replication branch: NAT-4.
6. **DEV-8** (G1-H hold margin), **DEV-9** (G7), **DEV-12** (periodic-reset check): see the table.

| Decision | Outcome |
|---|---|
| DEV-8 | thr + 3 by its rule (the high − mean over the 3 samples before t0 was 2-3 °C, 95th percentile 3); reported only |
| DEV-9 | not run (no D1 session) |
| DEV-12 | 2 RST runs (reset-ms 1000) climbed normally (one 700 MHz sample, no hold, no climb ending at 700); reported |

7. **DEVIATION-N1** (01:04): the NAT start window was opened at 01:05 instead of 02:30, since row 3's dry tests were
   done; candidates were inserted after each Z1.
8. **DEVIATION-N2** (01:45): after C1m, a dense Z1 watch every 2 min (passes 11xx) with a NAT candidate every 5th.
9. **DEVIATION-N3** (01:37): the NAT-1 session was ended early. At S = 65, 0 of 4 T-runs reached 800 MHz: the mean
   re-read 66 within 1 s of the edge.
10. **DEVIATION-N4:** NAT-1 is off, and a NAT session starts only at a reading ≤ 62 (later ≤ 60, NAT-4 only).
11. **DEVIATION-N5** (02:22): one continuation NAT-4 session with the final DEV-1 candidate fixed. It is p6041, which
    hit the Master Minion hang.
12. **FIX:** NAT candidate numbers 6102-6127 → 6041-6049 (block.sh accepts 6001-6099 only; p6101 failed rc 2 with no
    card access).
13. **STOP** (02:54): ALERT-MM-HANG; the queue and the night stopped.
14. **Tooling added for validation** (none of it changes development behaviour when `DV2_VAL` is unset):
    - `dv2lib.sh`/`dv2lib.py`/`block.sh` validation mode (`DV2_VAL=1`: data root dv2v/, the NAT session only with
      the frozen lock, no DEV-2/3 recompute, no RST, no level change);
    - `dv2v/` (block.sh VZ and VN, vn_check.py, reduce_val.py, val.json, prereg-val.json, LOCK.sha256);
    - dv2lib.py's night.json keys `nat1_off`, `nat_cool_max`, `nat_branches`, `nat_sessions_max`, `dev1_fixed`,
      `dev2_launch_s` and the dense-watch slots `z1b_first`/`z1b_period_s`.
15. **New items from development** (registered in PREREG-VAL): the idle items I1-I6 and the sign test G4-S.
    - The reducer maps SP time to host time through the DM request lines of the previous sampler, which fit within
      ±1.2 ms, with the SP clock drifting about 9 ppm.
    - When the ring holds no DM lines (at WARNING, e.g. after the admin's reset) it falls back to the uptime
      minutes (±30 s) and widens its margins. Tested on tonight's data: the same classification.

---

## 5. Readiness (PREREG-DEV §2) and what that means for the freeze

| Requirement | Status |
|---|---|
| ≥ 4 T-blocks under the final DEV-1 candidate at one branch | **2** (NAT-4) |
| C1m ≥ 3 blocks or the DEV-6 fallback | fallback |
| ≥ 2 ADD runs | yes (2 valid in p6038) |
| T1 on a real clock-change ring | the idle rings yes; `new OP` decoding no (the SP-line items are not registered) |
| T6 the retrospective reproduced | yes |

- **G4's band test** (TH5, which needs SD_dev from ≥ 4 blocks) stays in development: reported, not registered.
- **Registered anyway, as a named deviation from the readiness rule:** G1-T, G1-H, G2-C/D/U, G3-L/I and G4-S.
  - Their rules were frozen in PREREG-DEV §1 before any data, or are sign tests.
  - Their run parameters were fixed by DEV-1/2/3.
  - None depends on SD_dev, C1m or the SP-line parser.
