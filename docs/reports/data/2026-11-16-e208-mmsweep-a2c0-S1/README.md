# E208 session a2c0-S1, 2026-11-16: aifoundry2 card 0 under its governor: the model session's matmul sweep (1116-mmsweep), RAN FULL (85 of 85 runs)

*Mon 16 Nov 2026 (week 47), PST. **E208** is the model session's sweep 1116-mmsweep (another Claude session, working through a relay as the same lab user), **registered by its post on the round's Discussion, #10 at 18:25:03 PST**, whose forecast sha256 `087fa8fd3b6c9676a000e37274c0a7fef872c12a5952020f4c461c4b524541a2` is the freeze line; the lab's registration commit is `d005dc53` (20:26:46 PST; [`E208.md`](../../../../tools/claims-v3/e208/E208.md)), made after this session's data existed (the post, not the commit, is the registration). The model session ran this session itself, under its own claim (#10.1, posted 18:25:14 PST) and released it by its post #10.4 (19:08:43 PST). The lab's lane data-e208 (round Q200) then copied the session's files, checked them, reduced them with the registered reducer and commits them here, byte for byte. **The lab sent no command to the card**; nothing was set on it by anyone (the session's config reads at its start and end are equal).*

**Labels.** Every figure from the session is **measured** (the card's own records under `session/`). The arms, the schedule, the run forms, the windows, the stop lines and the reduction's rules are **registered** (by post #10 and the kit's source at its sha256s, E208.md). `checks-e208-a2c0-S1.*` is **the lab's desk check of the records** (this lane's `check_session_e208.py`, written for it). `data-e208-a2c0-S1.json` and `reduce-e208-a2c0-S1.txt` are **desk arithmetic of the measured records** by the registered reducer: not prices and not verdicts. **No forecast number is here:** the lab knows the model session's sealed forecast only by its sha256, and the model session scores it privately. (Each run record's `sched` entry carries the schedule's own planning figures, `est_peak_w` and `est_s`, registered with the kit's schedule; they are planning estimates, not the forecast.) The lab's desk steps ran under `/usr/bin/python3` 3.12.3 on aifoundry2.

## Departures and notes, dated (Mon 16 Nov 2026, PST)

1. **The freeze line came first.** Post #10 (the forecast's sha256) at 18:25:03.097; this session's first card command (its config read) at 18:25:26.071, **23.0 s later**; its claim #10.1 at 18:25:14.898, 11.2 s before that command. (Post times: the round's Discussion watcher's record, in UTC; session times: the session's own records.)
2. **The session started before the window its claim named.** #10.1 reads (its words, after the tag and his line, verbatim in part): "Claiming aifoundry2 card 0 for session S1 of the NDA box's matmul sweep 1116-mmsweep, from 18:28 to 19:55 PST, holding the card's lock for the whole window. The session is 85 runs over 71 arms (`src/sched/a2c0-S1.json`), about 58 card-minutes and at most 72." The session began at 18:25:22 (its box lock and checks), **2 min 38 s before 18:28**; its first card command, at 18:25:26.071, came **2 min 34 s before 18:28**; it ended at 19:04:51, inside the window. Its card-minutes (39.42) are within the claim's bound. Reported, not corrected: no other holder of the card was seen at any of the session's looks (et-who before the first card command and at the close, written in `etwho-before.txt` and `etwho-close.txt`; the identity read with the sampler; and, by the registered runner's code, et-who and ps before every run, where a finding stops the session: none did; checks C3, C5 and C7), and no lab lane had a card day on aifoundry2 (the orchestrator's yield of aifoundry2 to the model session's sweeps stood since 11:04:17).
3. **The release.** #10.4 (19:08:43 PST), its words in part: "Released aifoundry2 card 0 at 19:05 PST: session S1 ended cleanly at 19:04:51 (85 runs, 39.4 card-minutes, runner rc 0, nothing left running)." The lab copied the session only after it: 19:15:08 PST, on aifoundry2: a byte copy of the model session's sessions/1794882322-a2c0-S1/ (cp -a; diff -r equal; its MANIFEST.sha256 305 of 305 OK).
4. **The host binary on aifoundry2.** The claim names its sha256 (44895c13...); the kit's build record of the day, read by the lab here (`build-record-aifoundry2.json`, copied byte for byte: day 2026-11-16, BUILT at 15:40:14 PST), names host `44895c13...`, kernel ELF `aace138c...` (E136's pin) and reader `d1dea7a7...`; the binaries in the kit hash to those three (read by the lab at 20:27:58 PST); the session's runner checked all three against the record before its first card command (session.log line 3).
5. **Who checked what.** The model session's own gates ran on the box (the harness, the device-command audit, the identity gate and watch, the stops); the lab re-read their records and replayed the stop lines on every sample (checks C0-C8 below), and re-derived every run's time an op in the reduction's primary view from the raw launch records with its own code, written from the registered rule's words (`spot_time_e208.py`: "view win: 80 runs compared, worst relative difference 2.26e-16; 0 runs without a figure (0 of them on one side only); mismatches 0"). A verifier lane (verify-e208d) re-derives the reductions afterwards with its own code.

## The session

- **Card:** aifoundry2 card 0 under its own governor, as found; physical device ID 0; config at start and end (read, nothing set): TDP 65 W, temperature threshold 65 C, power state 3 (low_power), boot point 600 MHz, minion 519 mV.
- **When:** 18:25:22-19:04:51 PST Mon 16 Nov 2026 (session id `1794882322-a2c0-S1`); the opening rest 18:25:26-18:26:26 (599 samples, board median 21.98 W, die median 47 C, gate 55.0 C); **39.42 card-minutes**.
- **Runs:** 85 of 85 scheduled, in the schedule's order (`src/sched/a2c0-S1.json`, sha256 `c073cf501e19c28f...`): forms burst 72, null 5, sus3 8; roles anchor 9, arm 60, null 5, time 11; 72 arm names (71 arms and the anchor `4x8x8-int8-rnd`, run 9 times); after a three-process smoke (rc 0 each). 96 device processes (rgm136's host, each a 6 s process with `--budget 7.5` under a plain `timeout 10`), every one rc 0; 1,538 launches recorded, 1,346 counted by the reducer's launch rule.
- **Clock (every telemetry sample):** 23,619 samples: 600 MHz 17,582, 700 MHz 203, 800 MHz 5,834; inside the device processes' windows: 600 MHz 716, 700 MHz 198, 800 MHz 5,497. The governor moves the clock (600 MHz at rest; 700 and 800 MHz under load): the reducer's `win` view reads the 800 MHz launches 1.0-3.5 s into each process.
- **Peaks:** board 71.81 W; die (the shires' mean) 59 C; the hottest-sensor latch 61 C at first, 62 C at most.
- **Stops:** the live lines board above 85 W on 3 samples in a row, or the die at or above 80 C; the stop-path test at the start tripped both test lines and refused a start (its `STOPTEST-*` files); no live stop (status and queue `stop` null; replayed on every sample by the lab: 0 trips).

## The lab's checks (data-e208, `check_session_e208.py`; desk check of the records)

| check | verdict | what was read |
|---|---|---|
| C0 the source | PASS | the schedule's sha256 in session.log and queue.json = the registered `SRC-SHA256SUMS` entry = the file's; the session's harness line "HARNESS OK: 48 files at src/SRC-SHA256SUMS's sha256"; on aifoundry2 the kit's `src/` read by the lab: every file at that list, the list itself `543e9298d5a1013d...` = the registration's (equal at d005dc53), no file newer than 14:50:10 PST |
| C1 a clean end | PASS | runner.rc 0; the log's last line "session end"; status closing `ended`, runs 85/85/85 ran/done/total; runner.out = session.log byte for byte |
| C2 the runs | PASS | 85 run records against 85 scheduled, each its schedule entry; 96 processes, rc {'0': 96}; every process's launches ok, its result check ok, none stopped by file; flags none |
| C3 the identity | PASS | config reads and the sampler on `/dev/et0_mgmt` only; et-who with the sampler: {'other_off_card': 0, 'other_on_card': 0, 'ours_off_card': 0, 'ours_on_card': 2, 'ours_on_mgmt': 1}; 99 (smoke 3 + runs 96) host processes: each stderr names exactly one device, `/dev/et0_ops`, physical ID 0, and the runner's watch records nothing wrong; config start = end |
| C4 the clock | PASS | the minion clock present in all 23,619 samples (600 MHz 17,582, 700 MHz 203, 800 MHz 5,834) |
| C5 the stops | PASS | no live stop; the stop-path test ok; the lines replayed on every sample: 0 trips, 0 samples over the board line |
| C6 the timeouts | PASS | process rcs {'0': 96} (smoke {'0': 3}): no 124, 137 or 143; no kill, `timeout -k`, outlived or leftover word in any of the session's 307 text files |
| C7 no leftover | PASS | status and queue `leftover` null; no leftover line; et-who at the close 'no holder that blocks; no device process that blocks' |
| C8 the sampler | PASS | one start (sampler started (attempt 1, pid 134904, every 100 ms)), no restart; 23,619 samples over 39.42 min, median interval 100.0 ms, largest gap 125 ms, 12 slow reads; first sample 0.019 s after the first card command; every device process's window sampled |

**Verdict of the lab's checks: ALL PASS.** The desk check of code behind C6 (not a record of this session): the kit's runner wraps every device process in `timeout 10` with no `-k`, and its bounded waits end by SIGTERM only (E208.md's audit; the lab's grep of the registered source found no SIGKILL, `kill -9` or `timeout -k`).

## The reduction (the registered reducer; desk arithmetic of measured records)

`src/reduce_mms.py` (sha256 `b9e32618020d28a5...`, with its `mms_common.py` `c3fc7883544ad73c...`; both = the registration's, equal at d005dc53), copied from the kit and run unchanged from the copy at 19:20:31 PST under `/usr/bin/python3 -I -B` in the round's CPU slot: `reduce_mms.py 1794882322-a2c0-S1 --out data-e208-a2c0-S1.json --txt reduce-e208-a2c0-S1.txt` (rc 0; stderr empty; its printed table = the `.txt` byte for byte; the session copy unchanged before and after).

- **Primary view:** `win` (the 800 MHz launches 1.0-3.5 s into each process, pooled over the run's processes); 69 of the 69 runs of arms and the anchor carry an energy figure there; the 11 time-only runs carry none (never read for energy; 9 of them capped by the governor rule); the 5 null runs give the baseline rules' zero-signal readings.
- **The anchor** (`4x8x8-int8-rnd`, 9 runs): time an op 2.1690-2.1802 us; power over idle 18.07-18.63 W; energy over idle 38.29-39.60 nJ an op (mean 39.02, sd 0.44).
- **The die-start correction:** rule `default`, slope 0.0048 a degree (the anchors' own fit 0.00232 +- 0.00267 over a 4.00 C span), die reference 50.98 C.
- **The null runs** (the baseline rules at zero signal, W): burst.dP_bracket -0.013 (sd 0.028, n 5); burst.dP_line +0.049 (sd 0.060, n 5); burst.dP_plain -0.059 (sd 0.044, n 5); win.dP_bracket -0.003 (sd 0.027, n 5); win.dP_line +0.057 (sd 0.057, n 5); win.dP_plain -0.047 (sd 0.044, n 5).
- **Per arm and per run:** `reduce-e208-a2c0-S1.txt` (one line an arm: time an op, cycles an op, kernel clock, board, power over idle, energy an op and a multiply-add, the rails, the DDR droop, capped, the result check) and `data-e208-a2c0-S1.json` (every view of every run, the anchors, the nulls, the smoke).

## Files

| file | what | label |
|---|---|---|
| `session/` | the session's directory as the model session's runner wrote it, byte for byte (its own `MANIFEST.sha256` lists every file but itself, `runner.out` and `runner.rc`): the run records, every device process's stdout and stderr, the smoke, the identity, the config reads, the 10 Hz telemetry (`telemetry.jsonl.gz`), the stop-path test, the log | measured |
| `data-e208-a2c0-S1.json`, `reduce-e208-a2c0-S1.txt` | the registered reduction | desk arithmetic of measured records |
| `checks-e208-a2c0-S1.json`, `checks-e208-a2c0-S1.txt` | the lab's checks C0-C8 | desk check of the records |
| `check_session_e208.py` | the lab's checker (Python's own modules; reads only) | lab code |
| `spot_time_e208.py`, `spot-time-e208-a2c0-S1.txt` | the lab's re-derivation of every run's time an op in the primary view, and its printed line | desk check of the records |
| `build-record-aifoundry2.json` | the kit's build record of the day on aifoundry2, byte for byte | record |
| `SHA256SUMS` | every file here but itself | - |

Not copied: the session's detached start output beside its directory (`1794882322-a2c0-S1.start.out`, 0 bytes). Paths in the records are relative to the kit's top folder on the box (`build/`, `src/`, `sessions/`). No login and no home path is in any file here (the lab's scan, with the round's public-text scan).

## Reproduce

```
sha256sum -c SHA256SUMS
python3 -I -B check_session_e208.py session a2c0 ../../../../tools/claims-v3/e208/proposal/src --out checks.json --txt checks.txt
ln -s session 1794882322-a2c0-S1 && python3 -I -B ../../../../tools/claims-v3/e208/proposal/src/reduce_mms.py 1794882322-a2c0-S1 --out data.json --txt reduce.txt
python3 -I -B spot_time_e208.py session data-e208-a2c0-S1.json
```

The kit's source is the registration's proposal copy, [`tools/claims-v3/e208/proposal/src/`](../../../../tools/claims-v3/e208/proposal/src/) (E208.md, at the sha256s of its `SRC-SHA256SUMS`).
