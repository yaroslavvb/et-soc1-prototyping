# E208 session a1c1-S1, 2026-11-16: aifoundry1 card 1 at 600 MHz: the model session's matmul sweep (1116-mmsweep), RAN FULL (87 of 87 runs)

*Mon 16 Nov 2026 (week 47), PST. **E208** is the model session's sweep 1116-mmsweep (another Claude session, working through a relay as the same lab user), **registered by its post on the round's Discussion, #10 at 18:25:03 PST**, whose forecast sha256 `087fa8fd3b6c9676a000e37274c0a7fef872c12a5952020f4c461c4b524541a2` is the freeze line; the lab's registration commit is `d005dc53` (20:26:46 PST; [`E208.md`](../../../../tools/claims-v3/e208/E208.md)), made after this session's data existed (the post, not the commit, is the registration). The model session ran this session itself, under its own claim (#10.2, posted 18:25:18 PST) and released it by its post #10.5 (19:09:01 PST). The lab's lane data-e208 (round Q200) then copied the session's files, checked them, reduced them with the registered reducer and commits them here, byte for byte. **The lab sent no command to the card**; nothing was set on it by anyone (the session's config reads at its start and end are equal).*

**Labels.** Every figure from the session is **measured** (the card's own records under `session/`). The arms, the schedule, the run forms, the windows, the stop lines and the reduction's rules are **registered** (by post #10 and the kit's source at its sha256s, E208.md). `checks-e208-a1c1-S1.*` is **the lab's desk check of the records** (this lane's `check_session_e208.py`, written for it). `data-e208-a1c1-S1.json` and `reduce-e208-a1c1-S1.txt` are **desk arithmetic of the measured records** by the registered reducer: not prices and not verdicts. **No forecast number is here:** the lab knows the model session's sealed forecast only by its sha256, and the model session scores it privately. (Each run record's `sched` entry carries the schedule's own planning figures, `est_peak_w` and `est_s`, registered with the kit's schedule; they are planning estimates, not the forecast.) The lab's desk steps ran under `/usr/bin/python3` 3.12.3 on aifoundry2.

## Departures and notes, dated (Mon 16 Nov 2026, PST)

1. **The freeze line came first.** Post #10 (the forecast's sha256) at 18:25:03.097; this session's first card command (its config read) at 18:25:29.708, **26.6 s later**; its claim #10.2 at 18:25:18.282, 11.4 s before that command. (Post times: the round's Discussion watcher's record, in UTC; session times: the session's own records.)
2. **The session started before the window its claim named.** #10.2 reads (its words, after the tag and his line, verbatim in part): "Claiming aifoundry1 card 1 (`ET_DEVICES=1`) for session S1 of the NDA box's matmul sweep 1116-mmsweep, from 18:28 to 19:55 PST, holding the card's lock for the whole window, with nothing of ours on card 0 meanwhile. The session is 87 runs over 73 arms (`src/sched/a1c1-S1.json`), about 59 card-minutes and at most 72." The session began at 18:25:26 (its box lock and checks), **2 min 34 s before 18:28**; its first card command, at 18:25:29.708, came **2 min 30 s before 18:28**; it ended at 19:07:16, inside the window. Its card-minutes (41.78) are within the claim's bound. Reported, not corrected: no other holder of the card was seen at any of the session's looks (et-who before the first card command and at the close, written in `etwho-before.txt` and `etwho-close.txt`; the identity read with the sampler; and, by the registered runner's code, et-who and ps before every run, where a finding stops the session: none did; checks C3, C5 and C7), and no lab lane had a card day on aifoundry1 (the orchestrator's yield of aifoundry1 to the model session's sweeps stood since 11:04:17).
3. **The release.** #10.5 (19:09:01 PST), its words in part: "Released aifoundry1 card 1 at 19:09 PST: session S1 ended cleanly at 19:07:16 (87 runs, 41.8 card-minutes, runner rc 0, nothing left running)." The lab copied the session only after it: 19:15:29 PST: one read-only rsync from aifoundry1 of the model session's sessions/1794882326-a1c1-S1/ (rsync -a, rc 0; 314 files; its MANIFEST.sha256 311 of 311 OK).
4. **The host binary and the source on aifoundry1.** The claim names the host's sha256 (1ce00f1e...); the session's runner checked the host, the reader and the kernel against that box's build record of the day before its first card command (session.log line 3, the runner's box check). The lab read aifoundry1's kit itself only once no claim stood there (the orchestrator removed the aifoundry1 claim at 20:27 PST on the model session's #10.11): at 20:27:41 PST one read-only copy of its `src/` and build record, and at 20:27:59 PST one read-only sha256 of its three binaries. Its `src/` = the registered copy (`diff -r` equal; its `SRC-SHA256SUMS` `543e9298d5a1013d...` = the registration's, 48/48 OK); its build record (`build-record-aifoundry1.json`, copied byte for byte: day 2026-11-16, BUILT at 15:40:15 PST) names host `1ce00f1e...` (the claim's), kernel ELF `aace138c...` (E136's pin) and reader `e49c7143...`, and says the host, the reader and the device layer carry ET_DEVICES; the binaries on the box hash to those three now. These reads came after the session; what ties them to it: the files' modification times (the three binaries 15:40:12-15:40:15 PST, the build record 15:40:15 PST, every src file at or before 14:50:10 PST), all before the session, and the runner's own box check at its start.
5. **Who checked what.** The model session's own gates ran on the box (the harness, the device-command audit, the identity gate and watch, the stops); the lab re-read their records and replayed the stop lines on every sample (checks C0-C8 below), and re-derived every run's time an op in the reduction's primary view from the raw launch records with its own code, written from the registered rule's words (`spot_time_e208.py`: "view band600: 82 runs compared, worst relative difference 3.00e-16; 0 runs without a figure (0 of them on one side only); mismatches 0"). A verifier lane (verify-e208d) re-derives the reductions afterwards with its own code.

## The session

- **Card:** aifoundry1 card 1 at 600 MHz; physical device ID 1; config at start and end (read, nothing set): TDP 65 W, temperature threshold 65 C, power state 1 (managed_power), boot point 600 MHz, minion 499 mV.
- **ET_DEVICES:** the kit's runner sets `ET_DEVICES=1` for every device process on this card and its reader guard refuses any other value (desk check of the registered code); every host process's device layer enumerated card 1 alone (its stderr: one device block, `/dev/et1_ops`, physical ID 1), and the config reads and the sampler opened `/dev/et1_mgmt` alone (check C3).
- **When:** 18:25:26-19:07:16 PST Mon 16 Nov 2026 (session id `1794882326-a1c1-S1`); the opening rest 18:25:30-18:26:30 (598 samples, board median 30.56 W, die median 53.0 C, gate 56.0 C); **41.78 card-minutes**.
- **Runs:** 87 of 87 scheduled, in the schedule's order (`src/sched/a1c1-S1.json`, sha256 `1379fb656ccb281a...`): forms burst 74, null 5, sus3 8; roles anchor 9, arm 73, null 5; 74 arm names (73 arms and the anchor `4x8x8-int8-rnd`, run 9 times); after a three-process smoke (rc 0 each). 98 device processes (rgm136's host, each a 6 s process with `--budget 7.5` under a plain `timeout 10`), every one rc 0; 1,470 launches recorded, 1,274 counted by the reducer's launch rule.
- **Clock (every telemetry sample):** 25,032 samples: 600 MHz 25,032; inside the device processes' windows: 600 MHz 6,696. 600 MHz in every sample and in every counted launch (kernel clocks 599.1-599.6 MHz).
- **Peaks:** board 67.48 W; die (the shires' mean) 62 C; the hottest-sensor latch 66 C at first, 66 C at most.
- **Stops:** the live lines board above 75 W on 3 samples in a row, or the die at or above 80 C; the stop-path test at the start tripped both test lines and refused a start (its `STOPTEST-*` files); no live stop (status and queue `stop` null; replayed on every sample by the lab: 0 trips).

## The lab's checks (data-e208, `check_session_e208.py`; desk check of the records)

| check | verdict | what was read |
|---|---|---|
| C0 the source | PASS | the schedule's sha256 in session.log and queue.json = the registered `SRC-SHA256SUMS` entry (`543e9298d5a1013d...`, equal at d005dc53) = the registered file's; the session's harness line "HARNESS OK: 48 files at src/SRC-SHA256SUMS's sha256" (the box's own list); that list and every file of the box's `src/`, read by the lab at 20:27:41 PST once no claim stood: = the registered copy (note 4) |
| C1 a clean end | PASS | runner.rc 0; the log's last line "session end"; status closing `ended`, runs 87/87/87 ran/done/total; runner.out = session.log byte for byte |
| C2 the runs | PASS | 87 run records against 87 scheduled, each its schedule entry; 98 processes, rc {'0': 98}; every process's launches ok, its result check ok, none stopped by file; flags none |
| C3 the identity | PASS | config reads and the sampler on `/dev/et1_mgmt` only; et-who with the sampler: {'other_off_card': 0, 'other_on_card': 0, 'ours_off_card': 0, 'ours_on_card': 2, 'ours_on_mgmt': 1}; 101 (smoke 3 + runs 98) host processes: each stderr names exactly one device, `/dev/et1_ops`, physical ID 1, and the runner's watch records nothing wrong; config start = end |
| C4 the clock | PASS | the minion clock present in all 25,032 samples (600 MHz 25,032) |
| C5 the stops | PASS | no live stop; the stop-path test ok; the lines replayed on every sample: 0 trips, 0 samples over the board line |
| C6 the timeouts | PASS | process rcs {'0': 98} (smoke {'0': 3}): no 124, 137 or 143; no kill, `timeout -k`, outlived or leftover word in any of the session's 313 text files |
| C7 no leftover | PASS | status and queue `leftover` null; no leftover line; et-who at the close 'no holder that blocks; no device process that blocks' |
| C8 the sampler | PASS | one start (sampler started (attempt 1, pid 3877981, every 100 ms)), no restart; 25,032 samples over 41.77 min, median interval 100 ms, largest gap 101 ms, 0 slow reads; first sample 0.02 s after the first card command; every device process's window sampled |

**Verdict of the lab's checks: ALL PASS.** The desk check of code behind C6 (not a record of this session): the kit's runner wraps every device process in `timeout 10` with no `-k`, and its bounded waits end by SIGTERM only (E208.md's audit; the lab's grep of the registered source found no SIGKILL, `kill -9` or `timeout -k`).

## The reduction (the registered reducer; desk arithmetic of measured records)

`src/reduce_mms.py` (sha256 `b9e32618020d28a5...`, with its `mms_common.py` `c3fc7883544ad73c...`; both = the registration's, equal at d005dc53), copied from the kit and run unchanged from the copy at 19:20:42 PST under `/usr/bin/python3 -I -B` in the round's CPU slot: `reduce_mms.py 1794882326-a1c1-S1 --out data-e208-a1c1-S1.json --txt reduce-e208-a1c1-S1.txt` (rc 0; stderr empty; its printed table = the `.txt` byte for byte; the session copy unchanged before and after).

- **Primary view:** `band600` (the launches in the 600 MHz band); 82 of the 82 runs of arms and the anchor carry an energy figure there; the 5 null runs give the baseline rules' zero-signal readings.
- **The anchor** (`4x8x8-int8-rnd`, 9 runs): time an op 2.3630-2.3646 us; power over idle 9.47-9.77 W; energy over idle 21.86-22.56 nJ an op (mean 22.13, sd 0.24).
- **The die-start correction:** rule `default`, slope 0.0048 a degree (the anchors' own fit 0.00152 +- 0.00483 over a 2.08 C span), die reference 55.0 C.
- **The null runs** (the baseline rules at zero signal, W): band600.dP_bracket -0.004 (sd 0.038, n 5); band600.dP_line +0.053 (sd 0.026, n 5); band600.dP_plain -0.064 (sd 0.091, n 5); burst.dP_bracket -0.004 (sd 0.038, n 5); burst.dP_line +0.053 (sd 0.026, n 5); burst.dP_plain -0.064 (sd 0.091, n 5).
- **Per arm and per run:** `reduce-e208-a1c1-S1.txt` (one line an arm: time an op, cycles an op, kernel clock, board, power over idle, energy an op and a multiply-add, the rails, the DDR droop, capped, the result check) and `data-e208-a1c1-S1.json` (every view of every run, the anchors, the nulls, the smoke).

## Files

| file | what | label |
|---|---|---|
| `session/` | the session's directory as the model session's runner wrote it, byte for byte (its own `MANIFEST.sha256` lists every file but itself, `runner.out` and `runner.rc`): the run records, every device process's stdout and stderr, the smoke, the identity, the config reads, the 10 Hz telemetry (`telemetry.jsonl.gz`), the stop-path test, the log | measured |
| `data-e208-a1c1-S1.json`, `reduce-e208-a1c1-S1.txt` | the registered reduction | desk arithmetic of measured records |
| `checks-e208-a1c1-S1.json`, `checks-e208-a1c1-S1.txt` | the lab's checks C0-C8 | desk check of the records |
| `check_session_e208.py` | the lab's checker (Python's own modules; reads only) | lab code |
| `spot_time_e208.py`, `spot-time-e208-a1c1-S1.txt` | the lab's re-derivation of every run's time an op in the primary view, and its printed line | desk check of the records |
| `build-record-aifoundry1.json` | the kit's build record of the day on aifoundry1, byte for byte (read at 20:27:41 PST) | record |
| `SHA256SUMS` | every file here but itself | - |

Not copied: the session's detached start output beside its directory (`1794882326-a1c1-S1.start.out`, 0 bytes). Paths in the records are relative to the kit's top folder on the box (`build/`, `src/`, `sessions/`). No login and no home path is in any file here (the lab's scan, with the round's public-text scan).

## Reproduce

```
sha256sum -c SHA256SUMS
python3 -I -B check_session_e208.py session a1c1 ../../../../tools/claims-v3/e208/proposal/src --out checks.json --txt checks.txt
ln -s session 1794882326-a1c1-S1 && python3 -I -B ../../../../tools/claims-v3/e208/proposal/src/reduce_mms.py 1794882326-a1c1-S1 --out data.json --txt reduce.txt
python3 -I -B spot_time_e208.py session data-e208-a1c1-S1.json
```

The kit's source is the registration's proposal copy, [`tools/claims-v3/e208/proposal/src/`](../../../../tools/claims-v3/e208/proposal/src/) (E208.md, at the sha256s of its `SRC-SHA256SUMS`).
