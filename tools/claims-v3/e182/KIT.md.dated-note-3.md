# E182's kit, dated note 3: note 2's verifier's faults fixed before any E182 datum - step 6 v4 checks all nine build inputs before the build job and refuses a second build after a good one, every build's log and the day's count reach the data (step 11 v3), step 2 v4 pins this note's list, the re-run rule is labelled a stated departure, and the brief's E184 facts are brought up to date (Q154; new files only)

*Sat 7 Nov 2026 (week 45), on the Intel, desk only (Q154, lane `fix-e182n`; the lane began 18:38 PST and this note was first written at
19:02-19:03 PST; its commit's own time is git's): no card was claimed, no device command was sent, no lab box or mini was reached, nothing was
posted. It sits beside [KIT.md](KIT.md) (the kit, `41865c18`), [KIT.md.dated-note-1.md](KIT.md.dated-note-1.md) (`6c158cd2`) and
[KIT.md.dated-note-2.md](KIT.md.dated-note-2.md) (`22da6a7b`), which stay as committed, as do the registration ([E182.md](E182.md),
`58b88850`), its note 1 and every file of the four hash lists (32, 79, 50 and 49 OK after this note). It answers the adversarial verifier of
notes 1 and 2 (`verify-e182n`, 17:55-18:36 PST today: holds with fixes; 0 critical, 0 major, 4 minor, 3 nits): minors 1 and 2 (step 6 v4),
minor 3 ([E182.md.dated-note-2.md](E182.md.dated-note-2.md)), minor 4 and nit 7 ([CARD-LANE-BRIEF.md.dated-note-1.md](CARD-LANE-BRIEF.md.dated-note-1.md)),
nit 5 (step 6 v4 and step 11 v3) and nit 6 (section 7). It is committed before any E182 datum. **No forecast, threshold, statistic,
registered power figure, plan, cap or stop changes, and no file the box session runs changes:** `harness-e182.json` and
`harness-e182-note1.json` are unchanged, and so is every box file step 5 v2 sends. One rule's reading, when the fallback fires, was changed by
note 2 without saying so; E182.md.dated-note-2.md states it as a departure from the letter of E182.md section 7, before any datum.*

## Results first

- **Step 6 v4** ([`rb/s08_a3_preflight_e182_v4.sh`](rb/s08_a3_preflight_e182_v4.sh) `start | wait | --no-trains`) is step 6 v3 with three
  fixes:
  - **all nine build inputs are checked before the build job** (minor 1). v3's read before the build checked the 8 inputs beside main.cpp
    and note 1's 2 box files, so a main.cpp off its pin was caught only inside the job and spent a build. v4 also checks a scratch copy
    of the nine, as the build checks its own copy. A differing main.cpp now reads TRAIN-HOST-INPUTS-DIFFER before any job (16), with note
    1's words: step 5 v2 once more, then this step. No build is started or counted. If an input changes after that read and the job's own
    check finds it, the job reads TRAIN-HOST-INPUTS-DIFFER and is not counted, and wait says note 1's words.
  - **start is refused after a good build that day** (minor 2): 10, "the train host was built on aifoundry3 today". v3 started a second
    build, which removes the good host first, and if that build failed the trains were lost for the day.
  - **every build's own log is kept on the box,** and the box's count file gets one "ended" line per build with its result (nit 5).
- **Step 11 v3** ([`rb/s22_collect_e182_v3.sh`](rb/s22_collect_e182_v3.sh)) copies the count file and the day's build logs into the data's
  `logs/` (nit 5). Step 11 v2 copied only the last build's log.
- **Step 2 v4** ([`rb/s03_desk_e182_v4.sh`](rb/s03_desk_e182_v4.sh)) checks five hash lists at pinned counts, **32, 79, 50, 49 and 89**
  (this note's), and this note's desk test's log.
- **The faults, shown and fixed at the desk** ([`rb/selftest_rb_e182_v4.sh`](rb/selftest_rb_e182_v4.sh), **SELFTEST-RB-E182-V4 23 of 23
  PASS**, 300 s):
  - X2v: step 6 v3 builds with main.cpp off its pin, spends the day's first build and names no step 5. X2: step 6 v4 says
    TRAIN-HOST-INPUTS-DIFFER before any job, with note 1's words, and counts nothing.
  - X3v: step 6 v3 starts a second build after a good one; its failure leaves no host and names the fallback. X3: step 6 v4 refuses that
    start (10), and the host's sha256 is unchanged.
  - Cv: step 11 v2 copies neither the count file nor the first build's log. C: step 11 v3 copies the count file and both builds' logs.
- **The re-run rule is a stated departure** from the letter of E182.md section 7 and KIT.md box step 6 (minor 3), decided before any datum,
  in [E182.md.dated-note-2.md](E182.md.dated-note-2.md). It carries no bias: no datum can inform it, and a re-run builds the same pinned
  inputs.
- **The brief's dated note** ([CARD-LANE-BRIEF.md.dated-note-1.md](CARD-LANE-BRIEF.md.dated-note-1.md)) covers four things:
  - E184 now runs by its kit note 2 (`571511d0`), with six pinned lists, 11, 44, 6, 45, 3 and 20 (minor 4);
  - E182's steps 2 v4, 6 v4 and 11 v3;
  - after 11-14 on a step-6 start, run wait first;
  - the map from box steps to file numbers (nit 7).

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** KIT.md's block (INVENTORY.md read 13:30 PST), note 1's (16:05 PST) and note 2's (17:22 PST); this note re-read INVENTORY.md's
   rows for the pieces it takes, Sat 7 Nov 2026 at about 18:55 PST: H24 (the pool-8 card day, where the k6 runbook's v3 drivers ran), H27
   (E178's kit, whose form E182's is) and H28 (the kits' meter and stops). The row ids are opaque pointers into a private inventory. Pieces
   newer than it are cited by commit: E182's kit (`41865c18`) and notes 1 (`6c158cd2`) and 2 (`22da6a7b`); E184's A3 (`3b48cf7b`) and kit
   note 2 (`571511d0`).
2. **Used** (each unchanged, called, sourced, read or copied by path; sha256 in [`SHA256SUMS-e182-note3`](SHA256SUMS-e182-note3)):
   - **Note 2's step 6 v3** (`rb/s08_a3_preflight_e182_v3.sh`): v4 is it, line for line, with the changes its header marks v4.
   - **Note 1's box files**, called unchanged: `check_inputs_e182.py` (its tree mode, and its `--src` mode on a scratch copy, the check
     `build_host_e182_v2.sh` makes of its own copy), `build_host_e182_v2.sh` (inside the job, under the same `timeout -k 15 500`),
     `check_e182.py`, `preflight_e182.sh`, `e182_common.py`.
   - **Note 1's step 11 v2** (`rb/s22_collect_e182_v2.sh`): v3 is it with two more sources.
   - **The k6 runbook's v3 drivers** (`q141k-runbook/k6/rb_common.sh`: `ours_live`, `jobs_live`, `job_ok_today`, `rb_job_start`,
     `rb_job_wait`; v3.1's `rb_run.py` and its bounds) through `rb/rb_e182.sh`, unchanged.
   - **Note 2's desk test** (`rb/selftest_rb_e182_v3.sh`): its stand-in ssh, rsync and box, copied into the v4 test; its stand-in cmakes
     (`rb/fake_cmake_e182.sh`, `rb/fake_cmake_slow_e182.sh`) and Q139(k)'s mock runtime, unchanged.
   - **E184's kit note 2 and A3** (`../e184/KIT.md.dated-note-2.md` section 3, `../e184/E184.md.dated-note-A3.md`), read for the brief's
     note. *Check:* E184's step 2 v2 (`../e184/rb/s03_desk_e184_v2.sh`) pins its six lists at 11, 44, 6, 45, 3 and 20, and each list reads
     that many entries, all OK (`logs/reruns-note3.txt`).
3. **Not used:** rb_run.py's bound overrides; E172's card-1 kit; E180's code; the PVT sampler.
4. **Tiers:** every file of this note is public tier and cites public pieces only. No NDA-tier check enters it.
5. **Readiness:** this block is the note's. A verifier checks it against INVENTORY.md and the cited commits.

KIT.md's box steps are named by their numbers there (1 the window, 2 the desk check, 3 the post, 4 the look, 5 the sync, 6 the build and the
box's checks, 7 the reads, 8 the dry pass, 9 the session, 10 the wait, 11 the collection). The files are `rb/s02`, `s03`, k6's `s05`,
`s07`, `s08`, k6's `s09`, `s10`, `s11`, `s20` and `s22`.

## 1. Step 6 v4: all nine build inputs before the build job (the verifier's minor 1)

**The fault** (the verifier's case X2, reproduced here as X2v). Step 6 v3's read before the build ran `check_inputs_e182.py` in its tree
mode: the 8 build inputs beside main.cpp and note 1's 2 box files, not main.cpp. A main.cpp off its pin (`harness-e182.json`) was caught
only inside the job, by `build_host_e182_v2.sh`'s check of its own copy. The job read TRAIN-HOST-BUILD-FAILED, so wait counted the day's
first build and asked for the one re-run, which fails the same way and ends in the fallback. Note 1's re-sync words (step 5 v2 once more)
were never said; step 6 v2 had said them for the same box.

**The fix:**
- The read before the build runs the tree check as v3 does, and then copies the nine build inputs (`check_inputs_e182.py --list`) into
  `build/e182-inputs-copy/` and runs `check_inputs_e182.py --src` on it. That is the check the build makes of its own copy. It then removes
  the copy. Either check failing reads TRAIN-HOST-INPUTS-DIFFER (16) before any job. Note 1's rule then applies: an earlier build's host,
  copy and record are removed, and the step says "run step 5 v2 (rb/s07_a3_sync_e182_v2.sh) once more, then this step's start; if they
  differ again", then names the fallback. No build is started or counted, and the event is written in the count file as "not started".
- An input can still change between that read and the job's copy. Then the job's own check finds it, and the job reads
  TRAIN-HOST-INPUTS-DIFFER. It writes "ended rc=1: TRAIN-HOST-INPUTS-DIFFER ... (not a build)" in the count file, and that start is
  subtracted from the day's builds. wait then says note 1's words (16).

**The day's builds** are now the day's "started" lines less the jobs that ended TRAIN-HOST-INPUTS-DIFFER (they built nothing).
E182.md.dated-note-2.md states this reading of the registered fallback.

## 2. Step 6 v4: no second build after a good one (minor 2)

**The fault** (the verifier's X3, reproduced as X3v). Step 6 v3 did not refuse a start after a good build that day. `build_host_e182_v2.sh`
removes `src/`, `b/` and the record before it builds, so a second start removed the good host. It also spent the one re-run, and if that
build failed the step named the fallback and the trains were lost. A second start can come from an operator's repeat. It can also follow a
launch call cut after the job had started: the brief said to run the same sub-command again on 11, 12 or 13.

**The fix:** the read before the build refuses (10) when the job `a3-build-e182` ended rc 0 today (k6's `job_ok_today`), its output reads
TRAIN-HOST-BUILT, and the build record `build/e182host/SHA256` is there: "the train host was built on aifoundry3 today ...: run this step's
wait, which reads its checks". The refusal comes before the input check, so a good host is never removed. The brief's note says what to do
after 11-14 on start: run wait first, and start again only if wait reads JOB-UNKNOWN or the step asks for it.

## 3. The day's step-6 record reaches the data (nit 5)

**The fault.** Step 11 v2 copied `build/e182-build-host.txt` (the last build's log) but neither the box's count file
(`build/e182-build-attempts.txt`) nor the job's output. A re-run's start removes the first job's output, and the re-run's build overwrites
the log. So the data could not show the day's build count, or the first failed build's log, which the brief asks the data README to state.

**The fix, two halves:**
- **Step 6 v4's job** writes each build's own log to `build/e182-build-logs/<day>/e182-build-host-start<k>.txt`, where k is the day's k-th
  start. It writes the log there directly, so a lost job's partial log stays, and then copies it to `build/e182-build-host.txt` (v2's name,
  which v2's and v3's messages cite). It also writes one "ended rc=<b>: <result>" line per build to the count file.
- **Step 11 v3** (`rb/s22_collect_e182_v3.sh`) is v2 with two more sources: the count file and that day's directory of build logs. Both
  land in `build/e182-raw/logs/`, and `collect_e182.sh` copies every file there into the output's `logs/` (its line 122). A source the box
  does not hold is named in `absent-on-box.txt`, as v2 names any.

The data commit's public-text scan covers these logs with the other files, as it covers v2's copy of the build log.

**Step 6 v4's cosmetic words** (note 2's open issue): "the train host's build ran past its own N s bound", "the train host's build job was
lost". A job lost before it recorded its start reads "before the job recorded its start (no build recorded today)", where v3 read "build 0
of at most 2".

## 4. Step 2 v4: note 3's list pinned

Step 2 v4 is v3 with a fifth list at its pin, `SHA256SUMS-e182-note3` 89, and this note's desk-test log checked as committed. The pins are
written in the file, with no override. Desk cases P1 and P2 cover it. On a scratch repository holding every listed file, with an origin so
that the pull runs, v4 passes the intact tree. With note 3's list one line short, v4 refuses (16): "SHA256SUMS-e182-note3(88 OK of 88;
pinned 89)". Step 2 v3 passes the same tree, because it reads no note-3 list.

## 5. The re-run rule's label (minor 3)

Note 2's re-run rule reads E182.md section 7's "if the box's compile of the host-only change fails" as two failed builds on the day, and note
2 said that no rule changed. [E182.md.dated-note-2.md](E182.md.dated-note-2.md) states it as a departure from the letter of section 7 and of
KIT.md box step 6, decided before any datum and carrying no bias. It also states this note's two additions: a job that built nothing does
not count, and a good host is never rebuilt the same day. Nothing else of the rule changes.

## 6. The brief (minor 4 and nit 7)

[CARD-LANE-BRIEF.md.dated-note-1.md](CARD-LANE-BRIEF.md.dated-note-1.md) sits beside the brief, which stays as committed. It states four
things:
- E184 now runs by its kit note 2's table (`571511d0`): step 2 v2 with six pinned lists, step 7 v2, step 7 again after the session (10b),
  step 11 v2, and the look first. A3 (`3b48cf7b`) leaves E184's plan, caps and stops unchanged.
- E182's steps 2 v4, 6 v4 and 11 v3.
- What to do after 11-14 on a step-6 start.
- The map from KIT.md's box steps to the file numbers that note 1's v2 messages use.

## 7. Note 2's list (nit 6)

`SHA256SUMS-e182-note2` says it holds "the 35 unchanged files they call, source or read". It leaves out two that note 2's desk test uses:
`rb/s03_desk_e182_v2.sh` (run by its case P2) and the mock runtime's six headers (read by the stand-in compile). Both are pinned by note 1's
and the kit's lists, which step 2 checks, so nothing was unpinned. This note's list (89 entries) names every file its new steps call,
source or read on the card day, and every file its desk test runs or compiles beyond those, the mock runtime's headers among them. The
test's scratch copy of the lab's directories is the only exception.

## 8. The runbook as it now runs (KIT.md's box steps)

| KIT.md box step | file | changed here |
|---|---|---|
| 1, the window | `rb/s02_window_e182.sh` | no |
| 2, the desk check | **`rb/s03_desk_e182_v4.sh`** | v4 (section 4) |
| 4, the look, FIRST | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` | no (run before step 3: the brief) |
| 3, the post, after the look | (the card lane's) | no |
| 5, the sync | `rb/s07_a3_sync_e182_v2.sh` | no (note 1's v2) |
| 6, the build and the box's checks | **`rb/s08_a3_preflight_e182_v4.sh start`, then `wait`** (or `--no-trains`) | v4 (sections 1-3) |
| 7, the reads | `../q141k-runbook/k6/s09_a3_reads_k6.sh` | no |
| 8, the dry pass | `rb/s10_a3_dry_e182_v2.sh start|wait [--no-trains]` | no (note 1's v2) |
| 9, the session | `rb/s11_a3_session_e182_v2.sh FULL yes | PASSES no` | no (note 1's v2) |
| 10, the wait | `rb/s20_wait_e182.sh` | no |
| 11, the release, then the collection | **`rb/s22_collect_e182_v3.sh`** | v3 (section 3) |

v1's steps 2, 5, 6, 8, 9 and 11, v2's steps 2, 6 and 11, and v3's steps 2 and 6 are not run on the card day. Step 6 v3 must not be run on a
day step 6 v4 runs: it counts every line of the day in the count file, v4's "ended" lines with them, so it would refuse sooner, never later.
The dry listing of both paths is [`rb/list_steps_e182_v4.sh`](rb/list_steps_e182_v4.sh)
([`logs/dry-listing-e182-v4.txt`](logs/dry-listing-e182-v4.txt): 19 steps, 0 failing, the look listed before the post).

## 9. The checks, and what they re-ran

| check | result | log |
|---|---|---|
| the runbook v4 desk test (sections 1-4) | **SELFTEST-RB-E182-V4 23 of 23 PASS**, 300 s | `logs/selftest-rb-e182-v4.txt` |
| the dry listing v4, both paths | 19 steps listed, 0 failing, no call | `logs/dry-listing-e182-v4.txt` |
| dmcmd_audit, the runbook as it now runs with k6's steps 4 and 7 and the guard | GO, 11 send sites, every one READ | `logs/dmcmd-audit-rb-v4.txt` |
| dmcmd_audit, this note's desk files | GO, 0 send sites | `logs/dmcmd-audit-note3.txt` |
| the harness check and the frozen lists, after this note; E184's six lists at step 2 v2's pins | both makers CHECK PASS; HARNESS OK 66; NOTE1 FILES OK 10; 0 problems; registration 32/32, kit 79/79, note 1 50/50, note 2 49/49; no committed file edited since `22da6a7b` in E182's paths, the workload, E184's cited files or any path the four lists name; E184 11/11, 44/44, 6/6, 45/45, 3/3, 20/20 | `logs/reruns-note3.txt` |

The desk test's cases, in its own header: A (the dry listing), K (step 2 v4 without a window), P1 and P2 (the pins), S1 (step 6 v4 on a
synced stand-in box with the fast stand-in cmake), S2 (step 8 v2 on the box step 6 v4 left), X3 and X3v (minor 2), X2, X2v and X2r (minor 1),
X2b (an input that changes after the read: the job's own check, not counted), V4S (the 90 s cmake), O (a session of ours), R1-R4 (the re-run
rule, then the fallback through step 8 v2 `--no-trains`), C and Cv (nit 5), T (the build past its own bound), L (a lost job, its partial log
kept) and Z (nothing left running). On the stand-in box the four box binaries are stand-ins that refuse if run, and the box's copy of
`harness-e182.json` pins those stand-ins, as in note 2's test; after each step 5 v2 the test pins them again, because the sync puts the
committed pins back.

## 10. Labels

Every figure this note quotes from E182.md, its notes, the kit's notes and E184's kit (the caps, the plans, the stops, the pins) is
**registered**. The desk tests' results are checks of code at the desk, not measurements: nothing here is **blind** or **held out**, and no
E182 datum exists. The re-run rule's reading is a stated departure, registered in E182.md.dated-note-2.md.

## 11. For the verifier and the readiness critic

- The first real compile of the train host is still step 6 v4 on the box.
- Step 6 v4 adds box-side writes only under the tree's `build/`: the count file's lines, the day's build logs and a scratch copy of the
  nine inputs, which it removes. It opens no device, and every remote call stays inside rb_run.py's bounds.
- The collector has still not run end to end on a raw tree (KIT.md open item 3).
- Card time waits on his word.

**Compute:** on the Intel through the round's slot, one job at a time, at nice 10: the runbook v4 desk test, the listing, the audits and the
re-runs. No bench job, mini, lab box or card was used. The tests wrote only under the round's scratch (their scratch git repository and
stand-in box).

SPDX-License-Identifier: Apache-2.0
