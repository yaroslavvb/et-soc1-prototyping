# E182's kit, dated note 2: before any E182 datum, the train host's box build runs as one detached job with each check in its own bounded read, carries k6's refusal beside a session of ours and an at-most-one-re-run rule that ends in the registered fallback; step 2 pins every hash list's count; and the card lane's brief for the shared box (Q154; new files only)

*Sat 7 Nov 2026 (week 45), on the Intel, desk only (Q154, lane `e182n2`; the lane began 17:14 PST and this note was first written at
17:38 PST; its commit's own time is git's): no card was claimed, no device command was sent, no lab box or mini was reached, nothing was
posted. It sits beside [KIT.md](KIT.md) (the kit, `41865c18`) and [KIT.md.dated-note-1.md](KIT.md.dated-note-1.md) (`6c158cd2`), which stay
as committed, as do the registration ([E182.md](E182.md), `58b88850`) and every file of the three hash lists (32, 79 and 50 OK after this
note). It answers the Q153 readiness critic (`critic-q153`, Sat 7 Nov 2026 about 16:20-17:20 PST: E182 READY WITH GAPS), its faults 1-4.
It is committed before any E182 datum. **No rule, forecast, threshold, statistic, registered power figure, plan, cap or stop changes, and no
file the box session runs changes:** `harness-e182.json` and `harness-e182-note1.json` are unchanged, and so is every box file step 5 v2
sends. What it adds is desk files: runbook step 6 v3 and step 2 v3, the dry listing v3, a slow stand-in cmake, the runbook v3 desk test, the
card lane's brief ([CARD-LANE-BRIEF.md](CARD-LANE-BRIEF.md)), their logs and a hash list.*

## Results first

- **Step 6 v3** ([`rb/s08_a3_preflight_e182_v3.sh`](rb/s08_a3_preflight_e182_v3.sh) `start | wait | --no-trains`) runs the train host's
  first box build as **one detached job of the runbook**, E180's form (k6's `rb_job_start` / `rb_job_wait`), waited on with bounded waits;
  then `check_inputs_e182.py`, `check_e182.py`, the preflight and the verify, **each in its own 60 s read**. No call holds the build, so
  rb_run.py's bounds stay as they are (no `RB_READ_S`). Each call that works on the box is **refused beside a card session of ours** (k6's
  `ours_live`), and the start and the fallback beside any runbook job still running. **A build that failed, overran its own 500 s bound or
  was lost gets at most one re-run**; the box counts the day's builds, and after the second failure, or at a third start, the step names
  the registered fallback (PASSES, `--no-trains`) and stops.
- **The desk case the critic asked for, a stand-in cmake that sleeps 90 s** ([`rb/fake_cmake_slow_e182.sh`](rb/fake_cmake_slow_e182.sh)),
  past the 60 s read bound: **step 6 v2 is killed at its bound, twice** (13, "run this step again"; the box left with no train host and no
  record; the second run configured from scratch; the fallback never named), and **step 6 v3 passes it** (0: the job longer than 90 s,
  waits that said 17, the four checks each in a 60 s read, no call past a bound). The v2 runs' words and log lines are kept:
  [`logs/step6-v2-overrun-e182.txt`](logs/step6-v2-overrun-e182.txt).
- **Step 2 v3** ([`rb/s03_desk_e182_v3.sh`](rb/s03_desk_e182_v3.sh)) checks four hash lists against **pinned counts: 32, 79, 50 and 49**
  (this note's list). A kit list one line short is refused by v3 (16) and passed by v2 (its count read from the list itself).
- **The card lane's brief** ([`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md)): the look before the post in both runbooks (E182's and E184's);
  the shared-box order (E182 FULL, its step 11 copy-back, then E184 arm S's look; E184 arm B on aifoundry1 card 1 at any time, our only
  session there, never card 0); never E182's step 6 while a session of ours runs; step 6's re-run rule; E182-W-int8's verdict quoted as
  `size_P`.
- **The checks:** the runbook v3 desk test **SELFTEST-RB-E182-V3 16 of 16 PASS**; note 1's runbook desk test re-run unchanged,
  **SELFTEST-RB-E182-V2 19 of 19 PASS**; the dry listing v3, **19 steps, 0 failing**, no call; the harness check (both makers CHECK PASS,
  HARNESS OK 66, NOTE1 FILES OK 10, the three lists 32/79/50 OK, no committed file edited since `6c158cd2` in E182's paths or any path
  the lists name); `dmcmd_audit` **GO, 11 send sites, every one READ** for the runbook as it now runs, and GO with 0 sites for this note's
  desk files.

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** KIT.md's block (INVENTORY.md read 13:30 PST) and note 1's (16:05 PST); this note re-read INVENTORY.md's rows for the pieces
   it takes, Sat 7 Nov 2026 at about 17:22 PST: H24 (the pool-8 card day, where the k6 runbook's v3 drivers ran), H27 (E178's kit, whose
   form E182's is) and H28 (the kits' meter and stops). The row ids are opaque pointers into a private inventory. Pieces newer than it are
   cited by commit: E180's kit (`c92f627b`), its notes 1 (`90a1312f`) and 2 (`1e19a451`) and its card day (`c8a3a6ee`); E182's kit
   (`41865c18`) and notes 1 (`6c158cd2`); E184's kit note 1 (`eab0c70e`).
2. **Used** (each unchanged, called, sourced or copied by path; sha256 in [`SHA256SUMS-e182-note2`](SHA256SUMS-e182-note2)):
   - **E180's box build step** (`tools/claims-v3/e180/rb/s08_a3_build_e180_v2.sh`, its form only: the build as one detached job, waited on;
     it refuses during a session of ours). *Check against the same operation:* that step ran on aifoundry3 on 6 Nov 2026, its job
     12:53:49-12:53:53 PST, rc 0 (post hoc: E180's data README, `c8a3a6ee`, step 6).
   - **The k6 runbook's v3 drivers** (`q141k-runbook/k6/rb_common.sh`: `rb_prelude`, `ours_live`, `jobs_live`, `rb_job_start`,
     `rb_job_wait`, `rb_refused`; v3.1's `rb_run.py` and its bounds: a read 60 s, a launch 60 s, one wait 600 s) through `rb/rb_e182.sh`,
     unchanged.
   - **Note 1's box files**, called unchanged: `build_host_e182_v2.sh` (inside the job, under the same `timeout` bound of 500 s, with
     `-k 15` added so a build that ignores the first signal is killed), `check_inputs_e182.py`, `check_e182.py`, `preflight_e182.sh`,
     `e182_common.py`.
   - **Note 1's runbook desk test** (`rb/selftest_rb_e182_v2.sh`): re-run unchanged, and its stand-in ssh, rsync and box copied into the v3
     test; its stand-in cmake (`rb/fake_cmake_e182.sh`) is what the slow one runs after its sleep.
   - **E184's runbook table** (`../e184/KIT.md.dated-note-1.md` section 3), read for the brief.
3. **Not used:** rb_run.py's `RB_READ_S=600` for the one call (the critic's other option; rb_run.py calls its overrides "for the desk test
   only", and the detached job needs no bound raised); E172's card-1 kit; E180's and E184's code beyond the form above; the PVT sampler.
4. **Tiers:** every file of this note is public tier and cites public pieces only. No NDA-tier check enters it.
5. **Readiness:** this block is the note's. A verifier checks it against INVENTORY.md and the cited commits.

KIT.md's box steps are named by their numbers there (1 the window, 2 the desk check, 3 the post, 4 the look, 5 the sync, 6 the checks on the
box and the build, 7 the reads, 8 the dry pass, 9 the session, 10 the wait, 11 the collection); the files are `rb/s02`, `s03`, k6's `s05`,
`s07`, `s08`, k6's `s09`, `s10`, `s11`, `s20` and `s22`.

## 1. Step 6 v3: the build as one detached job, then each check in its own bounded read (the critic's fault 1)

**The fault** (the critic's words, checked here). Step 6 v2 (`rb/s08_a3_preflight_e182_v2.sh`) ran `check_inputs_e182.py`, the train
host's first cmake configure and build (`build_host_e182_v2.sh`, under `timeout 500`), `check_e182.py`, the preflight and the verify inside
ONE `rb_remote read`, which `rb_run.py` kills at 60 s (its `BOUNDS`, read 60). A build past that bound was killed and the step exited 13,
"run this step again"; every re-run rebuilt from scratch (the build removes `src/`, `b/` and the record first), and the step never read
TRAIN-HOST-BUILD-FAILED, so it never named the registered fallback. E180's box build took 4 s on 6 Nov (post hoc), so v2 would probably have
fit; no test had come near the bound.

**The fix, step 6 v3** (v2 stays as committed and is no longer run on the card day):
- **`start`:** after the probe, one bounded read: REFUSED (10) if a card session of ours runs on the box or a runbook job still runs; the
  number of train-host builds started there today (`build/e182-build-attempts.txt` on the box, by the Pacific calendar); the build inputs at
  their pins (note 1's check: if they differ, nothing is built, an earlier build's host, copy and record are removed, and the step stops
  with 16 and note 1's words: step 5 v2 once more, then this step; if they differ again, the fallback). Then the build as the detached job
  `a3-build-e182` (k6's `rb_job_start`, which refuses beside a session of ours too). The job records its start in that file, runs
  `timeout -k 15 500 bash tools/claims-v3/e182/build_host_e182_v2.sh`, and reads TRAIN-HOST-BUILT, or, after removing the failed build's
  host, copy and record, TRAIN-HOST-BUILD-FAILED, or TRAIN-HOST-BUILD-OVERRAN (rc 124 or 137: past its own bound).
- **`wait`:** one bounded wait (k6's `rb_job_wait`, at most 520 s on the box inside a 600 s call; 17 while the job runs: call `wait`
  again). When the job has ended rc 0: `check_inputs_e182.py` (NOTE1 FILES OK: 10 files), `check_e182.py` (HARNESS OK: 73 files),
  `preflight_e182.sh` (dmcmd_audit GO) and `e182_common.py --verify` (rc 0), **each in its own 60 s read**, each refused beside a session of
  ours. Any one failing stops the step (16) with v2's words ("a dated amendment first").
- **`--no-trains`:** the registered fallback's step 6, as v2's: no input check and no build; `check_e182.py --no-trains` (HARNESS OK: 70
  files), the preflight and the verify, each in its own 60 s read, refused beside a session or a job of ours.

**The re-run rule.** A build that failed, overran its own bound or whose job was lost (JOB-LOST: no process and no exit status) stops
`wait` with 16. The step reads the box's count of the day's builds: after the first it says "build 1 of at most 2 today: run this step's
start once more (the one re-run)"; after the second it names the fallback; a third `start` is refused (16) with the same words. The
fallback, in the step's words: step 6 v3 `--no-trains`, step 8 v2 `start --no-trains` then `wait --no-trains`, step 9 v2 `PASSES no`
(E182.md section 7: PASSES, cap 40 card-minutes, the post `for 1 h`; every train rule NOT SCORED). The count is the box's own: the job
writes its line when it starts, so a call cut by the network (11, 12 or 13) cannot add a build or hide one. This rule decides when "the
box's compile of the host-only change fails" (E182.md section 7) is read: after two builds that did not read TRAIN-HOST-BUILT on the day.

**What the desk can and cannot show.** `E182_BUILD_S` lowers the build's own bound for the desk test only; step 6 v3 reads it only with
`RB_DESKTEST=1` and refuses it otherwise (10), as step 11 v2 treats its collector stand-in. k6's job functions call every job "the dry
pass" in their messages (`rb_job_start`, `rb_job_wait`); here the job is the build. The real configure and build still need the box's SDK
and RISC-V toolchain: the first real compile is step 6 v3 on the box, as registered.

## 2. The desk case: a stand-in cmake that sleeps 90 s

[`rb/fake_cmake_slow_e182.sh`](rb/fake_cmake_slow_e182.sh) is note 1's stand-in with one change: its build phase first sleeps
`FAKE_CMAKE_SLEEP_S` seconds (90 by default). The runbook v3 desk test ([`rb/selftest_rb_e182_v3.sh`](rb/selftest_rb_e182_v3.sh), section 6)
runs it on the stand-in box with rb_run.py's own bounds (the test refuses to start if any `RB_<CLS>_S` is set):
- **V2O, the fault shown:** step 6 v2, twice. Each run is killed at its read bound and exits 13 after 61 s with "run this step again",
  the runbook log reading `class=read ... bound=60s secs=60.4 rc=13 ... status=timeout` (60.5 the second time); after each the box holds no train host and no build record; the
  second run configured from scratch; neither names the fallback; no build is left running.
  [`logs/step6-v2-overrun-e182.txt`](logs/step6-v2-overrun-e182.txt) keeps both runs' words and log lines.
- **V3S, the fix:** step 6 v3 on the same 90 s build: one job (a second `start` while it runs is refused, 10, and the day's count stays 1);
  four `wait`s with 30 s waits, three of them 17 while it ran; then the four checks: 0. The job took 95 s; all six of the step's reads (the
  two starts' and the four checks') ran under the 60 s bound, and no call ran past a bound.

## 3. Never beside a session of ours (the critic's fault 2, the code half)

Every v3 call that works on the box starts, after k6's prelude, with `REFUSED` when `ours_live` counts a card session of ours there; the
start and the fallback also refuse while any runbook job runs (`jobs_live`), and `rb_job_start` refuses beside a session again. The desk test's
case O makes the stand-in box report one session of ours: `start` stops after its probe and one read (10), the fallback and `wait`'s
checks stop (10), and no build is started or counted. E184's own build (its step 6, a detached job) and its session launch refuse beside a
session or job of ours by the same k6 functions; the brief states the order that keeps them apart.

## 4. Step 2 v3: every hash list's count pinned (the critic's fault 3)

Step 2 v2 pinned only the registration's 32 and read the kit's and note 1's counts from the lists themselves. Step 2 v3 is v2 with four
lists at pinned counts and no override: `SHA256SUMS-e182-registration` 32, `-kit` 79, `-note1` 50 and `-note2` 49; each must check OK in
full and hold exactly its pin. It also checks this note's two desk-test logs. Desk cases P1 and P2: on a scratch repository holding every
listed file (with an origin, so the pull runs), v3 passes the intact tree; with the kit's list one line short, v3 refuses (16,
"SHA256SUMS-e182-kit(78 OK of 78; pinned 79)") and v2 passes the same tree (0, "the three hash lists (32, 78 and 50)").

## 5. The card lane's brief (the critic's fault 2's order half, and fault 4)

[`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md), one file for the card day of both runs: before anything (his go, the approvals, one `RB_OUT`
per runbook and arm, one `RB_LOCK`); the order on the boxes; the look before the post in both runbooks; the day's one post and its
rewrites; step 6's re-run rule; the stops, commands and caps as registered; and the words the records use (E182-W-int8's verdict is
`size_P`; `size_E` is arm E's reading). It adds no rule.

## 6. The runbook as it now runs (KIT.md's box steps)

| KIT.md box step | file | changed here |
|---|---|---|
| 1, the window | `rb/s02_window_e182.sh` | no |
| 2, the desk check | **`rb/s03_desk_e182_v3.sh`** | v3 (section 4) |
| 4, the look, FIRST | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` | no (run before step 3: the brief) |
| 3, the post, after the look | (the card lane's) | the order only (the brief) |
| 5, the sync | `rb/s07_a3_sync_e182_v2.sh` | no (note 1's v2) |
| 6, the build and the box's checks | **`rb/s08_a3_preflight_e182_v3.sh start`, then `wait`** (or `--no-trains`) | v3 (sections 1-3) |
| 7, the reads | `../q141k-runbook/k6/s09_a3_reads_k6.sh` | no |
| 8, the dry pass | `rb/s10_a3_dry_e182_v2.sh start|wait [--no-trains]` | no (note 1's v2) |
| 9, the session | `rb/s11_a3_session_e182_v2.sh FULL yes | PASSES no` | no (note 1's v2) |
| 10, the wait | `rb/s20_wait_e182.sh` | no |
| 11, the release, then the collection | `rb/s22_collect_e182_v2.sh` | no (note 1's v2; its last line names E182-W-int8's verdict word) |

v1's steps 2, 5, 6, 8, 9 and 11, and v2's steps 2 and 6, are not run on the card day. The dry listing of both paths is
[`rb/list_steps_e182_v3.sh`](rb/list_steps_e182_v3.sh) ([`logs/dry-listing-e182-v3.txt`](logs/dry-listing-e182-v3.txt): 19 steps, 0
failing, the look listed before the post).

## 7. The checks, and what they re-ran

| check | result | log |
|---|---|---|
| the runbook v3 desk test (sections 1-4) | **SELFTEST-RB-E182-V3 16 of 16 PASS** | `logs/selftest-rb-e182-v3.txt` |
| note 1's runbook desk test, re-run unchanged (every v2 case) | **SELFTEST-RB-E182-V2 19 of 19 PASS** | `logs/selftest-rb-e182-v2-note2.txt` |
| step 6 v2 against the 90 s stand-in cmake (the fault, kept) | killed at the 60 s bound twice, 13 | `logs/step6-v2-overrun-e182.txt` |
| the dry listing v3, both paths | 19 steps listed, 0 failing, no call | `logs/dry-listing-e182-v3.txt` |
| the harness check and the frozen lists, after this note | both makers CHECK PASS; HARNESS OK 66; NOTE1 FILES OK 10; 0 problems; registration 32/32, kit 79/79, note 1 50/50; no committed file edited since `6c158cd2` in E182's paths, the workload, E184's note 1 or any path the three lists name | `logs/reruns-note2.txt` |
| dmcmd_audit, the runbook as it now runs with k6's steps 4 and 7 and the guard | GO, 11 send sites, every one READ | `logs/dmcmd-audit-rb-v3.txt` |
| dmcmd_audit, this note's desk files | GO, 0 send sites | `logs/dmcmd-audit-note2.txt` |

The desk test's cases, in its own header: A (the dry listing), K (step 2 v3 without a window), P1 and P2 (the pins), S1 (step 6 v3 on a
synced stand-in box with the fast stand-in cmake), S2 (step 8 v2 on the box step 6 v3 left), V2O and V3S (the 90 s cmake), O (a session of
ours), R1-R4 (the re-run rule, then the fallback through step 8 v2 `--no-trains`), T (the build past its own bound), L (a lost job) and Z
(nothing left running). On the stand-in box the four box binaries are stand-ins that refuse if run, and the box's copy of
`harness-e182.json` pins those stand-ins (the desk has no real binaries; on aifoundry3 the committed pins are E178's), so that step 6 v3's
harness check can read HARNESS OK 73 there; note 1's re-run test shows, with the committed pins, that only those four differ.

## 8. Labels

Every figure this note quotes from E182.md, its notes and E184's kit (the caps, the plans' card-minutes, the stops, the half-width, the
verdict words) is **registered**. E180's box build time on 6 Nov is **post hoc** (its committed data README).
The desk tests' results are checks of code at the desk, not measurements: nothing here is **blind** or **held out**, and no E182 datum
exists.

## 9. For the verifier and the readiness critic

- The first real compile of the train host is still step 6 v3 on the box; if it fails twice, the fallback runs to its end (note 1's F2-F4
  and this note's R4).
- The re-run rule adds wall time on the box (a second build, about as long as the first), never card time: the build opens no device,
  and the card-minutes count from the session's T0 (step 9).
- The collector has still not run end to end on a raw tree (KIT.md open item 3).
- Card time waits on his word.

**Compute:** on the Intel through the round's slot, one job at a time, at nice 10: the runbook v3 desk test 358 s (two 60 s
kills and one 90 s build of its own), note 1's re-run about 2 minutes, the listing, audits and re-runs seconds. No bench job, mini, lab box
or card was used. The tests wrote only under the round's scratch (their scratch git repositories and stand-in boxes).

SPDX-License-Identifier: Apache-2.0
