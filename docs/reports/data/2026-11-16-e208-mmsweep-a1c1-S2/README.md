# E208 session a1c1-S2, 2026-11-16: aifoundry1 card 1 at 600 MHz: the model session's matmul sweep (1116-mmsweep), RAN FULL (86 of 86 runs)

*Mon 16 Nov 2026 (week 47), PST. **E208** is the model session's sweep 1116-mmsweep (another Claude session, working through a relay as the same lab user), **registered by its post on the round's Discussion, #10 at 18:25:03 PST**, whose forecast sha256 `087fa8fd3b6c9676a000e37274c0a7fef872c12a5952020f4c461c4b524541a2` is the freeze line; the lab's registration commit is `d005dc53` (20:26:46 PST; [`E208.md`](../../../../tools/claims-v3/e208/E208.md)), made after this session's data existed (the post, not the commit, is the registration). The model session ran this session itself, under its own claim (#10.9, posted 19:39:51 PST) and released it by its post #10.11 (20:25:50 PST). The lab's lane data-e208 (round Q200) then copied the session's files, checked them, reduced them with the registered reducer and commits them here, byte for byte. **The lab sent no command to the card**; nothing was set on it by anyone (the session's config reads at its start and end are equal).*

**Labels.** Every figure from the session is **measured** (the card's own records under `session/`). The arms, the schedule, the run forms, the windows, the stop lines and the reduction's rules are **registered** (by post #10 and the kit's source at its sha256s, E208.md). `checks-e208-a1c1-S2.*` is **the lab's desk check of the records** (this lane's `check_session_e208.py`, written for it). `data-e208-a1c1-S2.json` and `reduce-e208-a1c1-S2.txt` are **desk arithmetic of the measured records** by the registered reducer: not prices and not verdicts. **No forecast number is here:** the lab knows the model session's sealed forecast only by its sha256, and the model session scores it privately. (Each run record's `sched` entry carries the schedule's own planning figures, `est_peak_w` and `est_s`, registered with the kit's schedule; they are planning estimates, not the forecast.) The lab's desk steps ran under `/usr/bin/python3` 3.12.3 on aifoundry2.

## Departures and notes, dated (Mon 16 Nov 2026, PST)

1. **The freeze line came first.** Post #10 (the forecast's sha256) at 18:25:03.097; this session's first card command (its config read) at 19:45:10.371, **80 min 7 s later**; its claim #10.9 at 19:39:51.556, 5 min 19 s before that command. (Post times: the round's Discussion watcher's record, in UTC; session times: the session's own records.)
2. **The claim and its window.** The round log records #10.9 as "claims aifoundry1 card 1 for S2, 19:45-21:12 PST (86 runs, 73 arms, about 58 card-minutes, at most 72; nothing on card 0 meanwhile)". The session ran 19:45:06-20:25:01 (first card command 19:45:10), inside the window (6 s after its start); its card-minutes (39.85) are within the claim's bound; no other holder of the card was seen at any of the session's looks (et-who before the first card command and at the close, written in `etwho-before.txt` and `etwho-close.txt`; the identity read with the sampler; and, by the registered runner's code, et-who and ps before every run, where a finding stops the session: none did; checks C3, C5 and C7), and no lab lane had a card day on aifoundry1 (the orchestrator's yield of aifoundry1 to the model session's sweeps stood since 11:04:17).
3. **The release.** #10.11 (20:25:50 PST), by the round log's record of it: "released aifoundry1 card 1: E208 a1c1-S2 ended cleanly 20:25:01 (86 runs, 39.9 card-minutes, rc 0, nothing left running)". The lab copied the session only after it: 20:27:20 PST: one read-only listing and one read-only rsync from aifoundry1 of the model session's sessions/1794887106-a1c1-S2/ (rsync -a, rc 0; 313 files; its MANIFEST.sha256 310 of 310 OK).
4. **The host binary and the source on aifoundry1.** The claim names the host's sha256 (1ce00f1e...); the session's runner checked the host, the reader and the kernel against that box's build record of the day before its first card command (session.log line 3, the runner's box check). The lab read aifoundry1's kit itself only once no claim stood there (the orchestrator removed the aifoundry1 claim at 20:27 PST on the model session's #10.11): at 20:27:41 PST one read-only copy of its `src/` and build record, and at 20:27:59 PST one read-only sha256 of its three binaries. Its `src/` = the registered copy (`diff -r` equal; its `SRC-SHA256SUMS` `543e9298d5a1013d...` = the registration's, 48/48 OK); its build record (`build-record-aifoundry1.json`, copied byte for byte: day 2026-11-16, BUILT at 15:40:15 PST) names host `1ce00f1e...` (the claim's), kernel ELF `aace138c...` (E136's pin) and reader `e49c7143...`, and says the host, the reader and the device layer carry ET_DEVICES; the binaries on the box hash to those three now. These reads came after the session; what ties them to it: the files' modification times (the three binaries 15:40:12-15:40:15 PST, the build record 15:40:15 PST, every src file at or before 14:50:10 PST), all before the session, and the runner's own box check at its start.
5. **Who checked what.** The model session's own gates ran on the box (the harness, the device-command audit, the identity gate and watch, the stops); the lab re-read their records and replayed the stop lines on every sample (checks C0-C8 below), and re-derived every run's time an op in the reduction's primary view from the raw launch records with its own code, written from the registered rule's words (`spot_time_e208.py`: "view band600: 82 runs compared, worst relative difference 3.70e-16; 0 runs without a figure (0 of them on one side only); mismatches 0"). A verifier lane (verify-e208d) re-derives the reductions afterwards with its own code.

## The session

- **Card:** aifoundry1 card 1 at 600 MHz; physical device ID 1; config at start and end (read, nothing set): TDP 65 W, temperature threshold 65 C, power state 1 (managed_power), boot point 600 MHz, minion 499 mV.
- **ET_DEVICES:** the kit's runner sets `ET_DEVICES=1` for every device process on this card and its reader guard refuses any other value (desk check of the registered code); every host process's device layer enumerated card 1 alone (its stderr: one device block, `/dev/et1_ops`, physical ID 1), and the config reads and the sampler opened `/dev/et1_mgmt` alone (check C3).
- **When:** 19:45:06-20:25:01 PST Mon 16 Nov 2026 (session id `1794887106-a1c1-S2`); the opening rest 19:45:10-19:46:11 (598 samples, board median 31.15 W, die median 54.0 C, gate 57.0 C); **39.85 card-minutes**.
- **Runs:** 86 of 86 scheduled, in the schedule's order (`src/sched/a1c1-S2.json`, sha256 `dc22d18d85751d18...`): forms burst 74, null 4, sus3 8; roles anchor 9, arm 73, null 4; 74 arm names (73 arms and the anchor `4x8x8-int8-rnd`, run 9 times); after a three-process smoke (rc 0 each). 98 device processes (rgm136's host, each a 6 s process with `--budget 7.5` under a plain `timeout 10`), every one rc 0; 1,470 launches recorded, 1,274 counted by the reducer's launch rule.
- **Clock (every telemetry sample):** 23,874 samples: 600 MHz 23,874; inside the device processes' windows: 600 MHz 6,682. 600 MHz in every sample and in every counted launch (kernel clocks 599.0-599.6 MHz).
- **Peaks:** board 67.75 W; die (the shires' mean) 62 C; the hottest-sensor latch 66 C at first, 66 C at most.
- **Stops:** the live lines board above 75 W on 3 samples in a row, or the die at or above 80 C; the stop-path test at the start tripped both test lines and refused a start (its `STOPTEST-*` files); no live stop (status and queue `stop` null; replayed on every sample by the lab: 0 trips).

## The lab's checks (data-e208, `check_session_e208.py`; desk check of the records)

| check | verdict | what was read |
|---|---|---|
| C0 the source | PASS | the schedule's sha256 in session.log and queue.json = the registered `SRC-SHA256SUMS` entry (`543e9298d5a1013d...`, equal at d005dc53) = the registered file's; the session's harness line "HARNESS OK: 48 files at src/SRC-SHA256SUMS's sha256" (the box's own list); that list and every file of the box's `src/`, read by the lab at 20:27:41 PST once no claim stood: = the registered copy (note 4) |
| C1 a clean end | PASS | runner.rc 0; the log's last line "session end"; status closing `ended`, runs 86/86/86 ran/done/total; runner.out = session.log byte for byte |
| C2 the runs | PASS | 86 run records against 86 scheduled, each its schedule entry; 98 processes, rc {'0': 98}; every process's launches ok, its result check ok, none stopped by file; flags none |
| C3 the identity | PASS | config reads and the sampler on `/dev/et1_mgmt` only; et-who with the sampler: {'other_off_card': 0, 'other_on_card': 0, 'ours_off_card': 0, 'ours_on_card': 2, 'ours_on_mgmt': 1}; 101 (smoke 3 + runs 98) host processes: each stderr names exactly one device, `/dev/et1_ops`, physical ID 1, and the runner's watch records nothing wrong; config start = end |
| C4 the clock | PASS | the minion clock present in all 23,874 samples (600 MHz 23,874) |
| C5 the stops | PASS | no live stop; the stop-path test ok; the lines replayed on every sample: 0 trips, 0 samples over the board line |
| C6 the timeouts | PASS | process rcs {'0': 98} (smoke {'0': 3}): no 124, 137 or 143; no kill, `timeout -k`, outlived or leftover word in any of the session's 312 text files |
| C7 no leftover | PASS | status and queue `leftover` null; no leftover line; et-who at the close 'no holder that blocks; no device process that blocks' |
| C8 the sampler | PASS | one start (sampler started (attempt 1, pid 3972166, every 100 ms)), no restart; 23,874 samples over 39.84 min, median interval 100 ms, largest gap 101 ms, 0 slow reads; first sample 0.02 s after the first card command; every device process's window sampled |

**Verdict of the lab's checks: ALL PASS.** The desk check of code behind C6 (not a record of this session): the kit's runner wraps every device process in `timeout 10` with no `-k`, and its bounded waits end by SIGTERM only (E208.md's audit; the lab's grep of the registered source found no SIGKILL, `kill -9` or `timeout -k`).

## The reduction (the registered reducer; desk arithmetic of measured records)

`src/reduce_mms.py` (sha256 `b9e32618020d28a5...`, with its `mms_common.py` `c3fc7883544ad73c...`; both = the registration's, equal at d005dc53), copied from the kit and run unchanged from the copy at 20:28:44 PST under `/usr/bin/python3 -I -B` in the round's CPU slot: `reduce_mms.py 1794887106-a1c1-S2 --out data-e208-a1c1-S2.json --txt reduce-e208-a1c1-S2.txt` (rc 0; stderr empty; its printed table = the `.txt` byte for byte; the session copy unchanged before and after).

- **Primary view:** `band600` (the launches in the 600 MHz band); 82 of the 82 runs of arms and the anchor carry an energy figure there; the 4 null runs give the baseline rules' zero-signal readings.
- **The anchor** (`4x8x8-int8-rnd`, 9 runs): time an op 2.3627-2.3651 us; power over idle 9.47-9.72 W; energy over idle 21.88-22.45 nJ an op (mean 22.15, sd 0.17).
- **The die-start correction:** rule `default`, slope 0.0048 a degree (the anchors' own fit 0.00384 +- 0.00360 over a 2.22 C span), die reference 55.0 C.
- **The null runs** (the baseline rules at zero signal, W): band600.dP_bracket -0.006 (sd 0.039, n 4); band600.dP_line +0.054 (sd 0.051, n 4); band600.dP_plain -0.067 (sd 0.082, n 4); burst.dP_bracket -0.006 (sd 0.039, n 4); burst.dP_line +0.054 (sd 0.051, n 4); burst.dP_plain -0.067 (sd 0.082, n 4).
- **Per arm and per run:** `reduce-e208-a1c1-S2.txt` (one line an arm: time an op, cycles an op, kernel clock, board, power over idle, energy an op and a multiply-add, the rails, the DDR droop, capped, the result check) and `data-e208-a1c1-S2.json` (every view of every run, the anchors, the nulls, the smoke).

## Files

| file | what | label |
|---|---|---|
| `session/` | the session's directory as the model session's runner wrote it, byte for byte (its own `MANIFEST.sha256` lists every file but itself, `runner.out` and `runner.rc`): the run records, every device process's stdout and stderr, the smoke, the identity, the config reads, the 10 Hz telemetry (`telemetry.jsonl.gz`), the stop-path test, the log | measured |
| `data-e208-a1c1-S2.json`, `reduce-e208-a1c1-S2.txt` | the registered reduction | desk arithmetic of measured records |
| `checks-e208-a1c1-S2.json`, `checks-e208-a1c1-S2.txt` | the lab's checks C0-C8 | desk check of the records |
| `check_session_e208.py` | the lab's checker (Python's own modules; reads only) | lab code |
| `spot_time_e208.py`, `spot-time-e208-a1c1-S2.txt` | the lab's re-derivation of every run's time an op in the primary view, and its printed line | desk check of the records |
| `build-record-aifoundry1.json` | the kit's build record of the day on aifoundry1, byte for byte (read at 20:27:41 PST) | record |
| `SHA256SUMS` | every file here but itself | - |

Not copied: the session's detached start output beside its directory (`1794887106-a1c1-S2.start.out`, 0 bytes). Paths in the records are relative to the kit's top folder on the box (`build/`, `src/`, `sessions/`). No login and no home path is in any file here (the lab's scan, with the round's public-text scan).

## Reproduce

```
sha256sum -c SHA256SUMS
python3 -I -B check_session_e208.py session a1c1 ../../../../tools/claims-v3/e208/proposal/src --out checks.json --txt checks.txt
ln -s session 1794887106-a1c1-S2 && python3 -I -B ../../../../tools/claims-v3/e208/proposal/src/reduce_mms.py 1794887106-a1c1-S2 --out data.json --txt reduce.txt
python3 -I -B spot_time_e208.py session data-e208-a1c1-S2.json
```

The kit's source is the registration's proposal copy, [`tools/claims-v3/e208/proposal/src/`](../../../../tools/claims-v3/e208/proposal/src/) (E208.md, at the sha256s of its `SRC-SHA256SUMS`).
