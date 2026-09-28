# DV2: DVFS and heat on aifoundry2, the development night of 27-28 September 2026

**Status: development data, not validated.** These runs chose the parameters and the rules of a validation plan that
was frozen afterwards (`plan/PREREG-VAL.md`). They test nothing. The validation has not run (below). The DVFS page
reports them in its section 8, labelled as development throughout
(`docs/reports/2026-09-22-dvfs-leakage.html#what-triggers-a-step-down-and-does-placement-delay-it`).

**The owner's questions** (27 September, 21:50 PDT): does voltage-frequency scaling act on the average temperature or
on one hot shire, and can the same computation run longer before it is throttled in some places on the chip?

**Card.** aifoundry2 only (firmware release 1.3.1, service-processor bootloader 0.20.0), the only card whose governor
moves the clock. Nothing on aifoundry1. aifoundry3 had one read-only query (Z2, 00:33 PDT: uptime, the throttle-state
residencies, configuration, the trace ring); its output is still on aifoundry3
(`~/nekko/build/claims-v3/aifoundry3/dv2/z2-20260928T003343/z2.json`) and is not in this directory; its result is recorded
in `plan/DEV-RESULTS.md` §3 (TH8).

**Nothing was set on the card:** no threshold, TDP, active power management, clock or voltage; the service
processor's log level was never changed (the sessions' level check read WARNING_OR_LOWER, a misreading of a card at
INFO, so nothing was set or restored: `plan/DEV-RESULTS.md` §4, DEV-5); no reset was attempted.

## What ran (PDT, 28 September 2026)

| Time | Pass | What | Card time |
|---|---|---|---|
| 00:40-02:54 | Z1 `p1001`-`p1012`, `p1101`-`p1112` | 21 read-only watch cycles, every 10 min from 00:40, every 2 min from 02:32. Three 10-minute slots did not run: `p1007` (01:40; the night stop set at the end of NAT-1 was still in place: `queue-dv2-aifoundry2.log`, 01:38:15, "nothing runs"; no directory) and `p1010`, `p1011` (02:10, 02:20; their slots passed while `p6038` held the card: their `block.json`). Each: the gate (`who`, the process scan, `et-who`, the use count); `flock -n` on the card lock; `ettelem sptrace` (the SP's 4 KB trace ring, `sp.bin`); the residencies of throttle states 2-6 and the uptime (`z2-*.jsonl`); `config` (`config.json`, the threshold read 65 every time); one 1 s, 10 Hz `ettelem sample` with one statistics reset at its start (`tel.jsonl`); the summary `z1.json` | about 1.5 s each |
| 01:30-01:38 | NAT `p6035` | NAT-1 (start reading 64 °C): probe, smoke, the power-adder run (ADD), one T-block. Ended early by DEVIATION-N3: from S = 65 none of its 4 runs reached 800 MHz | 7.5 min |
| 02:00-02:25 | NAT `p6038` | NAT-4 (60 °C): probe, smoke, ADD, 3 T-blocks of 4 runs (block 1 at 128 minions, blocks 2-3 at 192 after DEV-1), 2 runs with a periodic statistics reset (RST), ADD | 25 min |
| 02:30 | smoke `p4001` | one 2 s UNI32@4 launch | 18 s |
| 02:31 | C1m `p5001` | skipped by its own rule: a Z1 reading of 64 °C or less within 60 min | 0 |
| 02:50-02:51 | NAT `p6041` | continuation NAT-4 (59 °C): probe, smoke, then the Master Minion hung at the second lift of its ADD run (below) | 53 s |

`host-sensors.jsonl.gz` is the host's own `sensors -j` every 60 s (00:34-02:52; `tools/claims-v3/dv2/hostlog.sh`, no card
access). `dev-log.jsonl` is every development decision (DEV-n) and deviation (DEVIATION-Nn) with its data;
`nat-candidates.jsonl` the NAT start checks; `ALERT-MM-HANG.json`, `NIGHT-STOP` and `sp-level.json` the night's stop and
log-level records. Beside `raw/`: `queue-dv2-aifoundry2.log`, the queue's own log of the night (a copy of
`build/claims-v3/queue-dv2-aifoundry2.log`, unchanged), which is the only record of a pass that never started (`p1007`);
and `incident/`, the host's kernel-log error events for the card with the calibration of their times (below).

**A T-run** (`tools/claims-v3/dv2/block.sh`; the observables `tools/claims-v3/dv2/dv2obs.py`, computed live into
`runs.jsonl`): lifts until the mean reads S+1; the falling S+1 → S edge (S = 62 in NAT-4) with a one-shot statistics reset
at S+1, which restarts the sensors' peak-hold marks; one launch (8 s; 7 s in block 1) of `sparsity_host` (random fp32
multiply-add) in one of the placements of `tools/claims-v3/dv2/placements.json` (B4C@32, INT16@N, PER16@N, UNI32@4); the
stop 2.0 s after the first 800 → 700 MHz step; a 10 s tail; `sptrace`; the post-run clock check. Files per session:
`session.json`, `block.json`, `marks.jsonl` (every event), `launches.jsonl` (every heater process), `runs.jsonl`,
`tel-<idx>.jsonl.gz` (10 Hz samples), `heater-<idx>[-pre].out.gz` (heater output), `sp-*.bin` (trace-ring dumps),
`global-state.jsonl`, `config-*.json`, `z2-*` (residency and uptime reads), `code.sha256`, `binaries.json`,
`manifest.txt`, `mgmt.log.gz` (the device configuration), `probe/` (the R0 probe: `p0.bin`, `et-who.txt`).

## Where it came from

`raw/` is a copy of `aifoundry2:~/claude/et-soc1-dvfs2/build/claims-v3/aifoundry2/dv2/` (branch `dvfs2`), taken on
28 September at about 03:15 PDT after the queue stopped. Two changes, both lossless: `host-sensors.jsonl` and every
`mgmt.log` are gzipped (`gzip -9n`); nothing is renamed, so the reducers below read `raw/` as they read the original.
The tools are in `tools/claims-v3/dv2/` (the night) and `tools/claims-v3/dv2v/` (the frozen validation); how the night
was started is in `tools/claims-v3/dv2/README.md` ("Start") with the queue `tools/claims-v3/schedule-dv2-aifoundry2.txt`.

## The plan (`plan/`)

| File | What |
|---|---|
| `DESIGN.md` | the design, revision 2 (27 Sep, about 23:40 PDT): theories TH1-TH8, observables, runs |
| `PREREG-DEV.md` | the development pre-registration (27 Sep, about 23:55 PDT, before any DV2 card work): what development may decide and by which rule |
| `PREREG-VAL.md` | **the frozen validation plan** (28 Sep, about 03:15 PDT). SHA-256 `e150ce1620c1a9c5551d17206463020eab1ad2d226efe46dbb3fac3a53e2ffd1` (`PREREG-VAL.sha256`; `sha256sum -c PREREG-VAL.sha256`) |
| `LOCK.sha256` | the lock the plan registers: the SHA-256 of every file a validation pass runs; its own SHA-256 is `6ca61de1ed62678842a24bd94be17ca71f18fb52f09866aa7546f11721e34dea`. Every pass runs `sha256sum -c` on it and refuses to start on any difference |
| `prereg-val.json`, `val.json` | the frozen numbers and the validation schedule's window (copies of `tools/claims-v3/dv2v/`). G4's prediction (`L_pred` 0.28 ± 0.10) is computed from `g4.inputs`, whose couplings (`L600_PER_INT` 0.48, `L600_UNI_INT` 0.34) come from aifoundry3's heat-placement runs of 27 September; those runs' data are not yet in the repository |
| `DEV-RESULTS.md` | the development results as written at the freeze (28 Sep, about 03:10 PDT) |
| `review-governor.md` | the governor the cards run, read line by line at et-platform `ffca4cbb4` (0.20.0), `da192816a` (0.18.0) and `353f20e` (the rewrite), with what the three cards show |

The files are byte-identical copies (the originals: `tools/claims-v3/dv2v/` for `PREREG-VAL.md`, `DEV-RESULTS.md`,
`LOCK.sha256`, `prereg-val.json` and `val.json`; the session's scratch notes for the other three).

**Why the validation has not run.** (1) It is a replication on aifoundry2 in a later session, since no other card's
governor moves the clock (aifoundry3's is stuck at its 0 W TDP, aifoundry1's card 1 does not act); the owner has to
accept that, and pick the full schedule (watch plus heating sessions) or the idle-only one. (2) The heating sessions need
aifoundry2's Master Minion, which hung (below) and only the lab admin can restore. The read-only watch does not use it.
Earliest start: 12:00 PDT on 28 September. The commands are in `plan/PREREG-VAL.md` §6.

## The incident: aifoundry2's Master Minion hung, 28 September 2026, 02:50:53 PDT

- In `p6041`, the ADD run's lift 1 (UNI32@4, 7 s) ran normally: 800 MHz, "device held for 7.46 s".
- A lift is not one 7 s kernel: the heater (`sparsity_host`) runs a 20,000-iteration calibration kernel and then a stream
  of short kernels for about 7 s (lift 1: a 19 ms calibration kernel at 0.58 GHz, then 19 kernels of 0.37-0.49 s,
  `heater-1-pre.out.gz`).
- Lift 2 was launched 0.60 s after lift 1 ended, with the clock still at 800 MHz; the host read the idle reset's 600 MHz
  0.13 s later (02:50:53.725), and the device was ready 0.15 s after the launch. Lift 2's calibration kernel then ran,
  21 ms after that reading: 02:50:53.746-.761, `ok: true`, measuring 0.77 GHz, between the two points. The next kernel,
  the first of the stream, never completed: from 0.93 s the board read the 26 W idle and the clock stayed at 600 MHz;
  "kernel did not finish within 6 s, aborting the stream"; `timeout 10` stopped the process (rc 124).
- Lifts 3 and 4 failed at runtime creation: "Couldn't use the HPSQ. Perhaps the Master Minion is hanged?" (rc 1). After
  three heater failures the session aborted, and the queue was stopped (`ALERT-MM-HANG.json`, `NIGHT-STOP`).
- The host's kernel log (`incident/kernel-log.txt`, the card's error events from `dmesg`, read on 28 Sep about 03:20
  PDT): "Error Event Detected, Level Critical, SP Runtime Error, Runtime Error Count Beyond Threshold: 6" at
  **02:50:57.6 ± 0.07 s**, 3.9 s after lift 2's calibration kernel ended. That time comes from the event's boot-relative
  stamp (817669.211747 s) mapped with the audit records around it (`incident/clock-anchors.txt`: each record's
  boot-relative stamp and the epoch time the kernel wrote into it), interpolated between the one 2.8 h before and the one
  10 min after; the ± is half the difference between those two records' offsets. `dmesg -T` prints 02:51:07 because it
  adds every stamp to one boot time, and the boot-relative clock drifts against the wall clock (about 0.044 s per hour).
  The driver logs an event when it reads it, so the service processor may have counted the error earlier. Reproduce:
  `python3 incident/kernel_events.py` (`incident/kernel-events.out` is its output). The same counter reached 1 and 2 on
  20 September, 3 and 4 on 22 September and 5 on 25 September, and those did not stop the card, so the sixth need not
  be the hang's.
- The service processor still answers: the watch cycles at 02:52 and 02:54 read 600 MHz, 25.9 and 25.8 W, a mean of
  60 °C and the threshold at 65.
- No reset was attempted (the card rules). The lab admin must restore the Master Minion; until then no kernel can run on
  aifoundry2.
- **The cause is not established.** The 43 heater launches before it that night all ran (`raw/p*/launches.jsonl`: 46
  records in all, the hung lift and the two runtime-creation failures after it included). That the launch met the
  governor's clock change is a hypothesis.

The numbers above are from `dv2.json` (`cards.aifoundry2.incident`: `lifts[].calib`, `lifts[].stream`, `lift2`,
`kernel_log`, `kernel_log_last`), which `build_dv2_data.py` computes from `raw/p6041/` and `incident/`.

## Errata to the frozen `plan/DEV-RESULTS.md`

`plan/DEV-RESULTS.md` is the development record as frozen with the plan, and it stays byte-identical. Where the data
say otherwise, the data hold (the page and the knowledge base follow them):

- §2, the incident: "Its kernel never started". Lift 2's calibration kernel ran and returned ok (02:50:53.746, 14 ms,
  0.77 GHz); the kernel that never completed is the next one, the first of the stream (`heater-1-pre.out.gz`;
  `dv2.json` `incident.lifts[1].calib`, `incident.lift2`). The alert written at the time, `raw/ALERT-MM-HANG.json`
  ("never started its kernel", kept as written), takes the same correction.
- §2, "Cause": "Tonight's other 45 heater launches (probes, smokes, lifts 0.3-0.6 s apart, runs) ... never hung". The
  night has 46 launch records: 43 ran before the hang, all rc 0 (`incident.launches_before`), then the hung lift and two
  runtime-creation failures. The earlier lift-to-lift gaps were 0.52-0.58 s (four; the hung one 0.60 s).
- §3, "The rest swings": "The host saw no change. Its sensors were flat: ACPI 16.8 and 27.8 °C, NVMe 43-45 °C". The ACPI
  zones read constant (probably not live readings), but the NVMe drive read 42.9-46.9 °C and the CPU package 37-59 °C
  over 139 readings, 00:34-02:52 (`dv2.json` `host_sensors`). What drives the swing is not established.
- §3, TH3: "repeated for up to 4 s". The longest crossing lasted 3.6 s (3.612 s; `dv2.json` `lines.crossings`).

## Reductions and the page's data

From the repository root (none of these touches a card):

```bash
V=docs/reports/data/2026-09-28-dvfs2-aifoundry2
python3 tools/claims-v3/dv2/reduce_dv2.py --dev --data $V/raw --out $V/reductions/dv2-dev.json
python3 tools/claims-v3/dv2v/reduce_val.py --data $V/raw --dev --out $V/reductions/dev-idle.json
python3 tools/ettelem/build_dv2_data.py --data $V                     # writes $V/dv2.json and prints its main numbers
python3 tools/ettelem/build_dv2_data.py --data $V --merge docs/reports/data/2026-09-22-dvfs-aifoundry2/dvfs.json
```

- `reductions/dv2-dev.json`: the development reducer (Z1, the sessions, the host bands G2-C/D/U, ADD's P_U, G4, the
  decision log, readiness). Its G4 (`L_dev` 0.52) counts a run that held to the end as the launch length and includes every
  INT16/PER16 block; the frozen rule (below) does not.
- `reductions/dev-idle.json`: the frozen validation reducer run on the development data (`--dev`): the idle items I1-I6
  and the NAT items with the frozen rules. Its verdict words on development data mean nothing; its counts are what the page
  quotes. It records the time it ran (`"t"`), so a rerun differs in that field only.
- `dv2.json`: the page's reduction (`tools/ettelem/build_dv2_data.py`, deterministic): the watch cycles, the sessions, every
  governor line with host time, the crossings, the loop intervals against 0.4053 s, the T-runs with a 10 Hz excerpt,
  Q1 (G1-T, G1-H), Q2 (G4 by the frozen rule: a held run counts to its kernel's end), the host bands, the latencies, the
  residency counters, the host sensors, the incident, the placements' grid, the plan's SHA-256 and the decision log.
- One caution the page states: the frozen reducer accepts an SP-to-host time fit made from a single DM request line; in
  this data one such fit (dump `p1008`) matched a session sampler's line and is 474 s off the other 15 (which agree within
  1.2 ms). `build_dv2_data.py` sets fits more than 1 s from the median aside; `reduce_val.py` is frozen and does not. In
  `reduce_val.py`'s own run on the watch dumps the bad fit moves no thermal line (checked by mapping every line with and
  without it); with the session dumps added it would move the one session-time crossing, 01:30:27, to 01:22:33. The
  validation meets the same risk whenever a session runs between two watch cycles.

The page itself: `python3 scripts/build-report.py dvfs-leakage docs/reports/data/2026-09-22-dvfs-aifoundry2/dvfs.json
docs/reports/2026-09-22-dvfs-leakage.html` (the full chain is in the page's "Reproduce this").
