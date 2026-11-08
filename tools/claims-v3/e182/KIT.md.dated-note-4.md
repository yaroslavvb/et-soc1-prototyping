# E182's kit, dated note 4: note 3's verifier's fault fixed before any E182 datum - step 6 v5 reads a cut wait call as no reading (14, wait again), never a failed build, refuses the fallback beside a good train host, and reads a cut check as no reading; step 2 v5 pins this note's list; dated note 3 corrects E182.md's note 2; the brief's note 2 (Q155; new files only)

*Sat 7 Nov 2026 (week 45), on the Intel, desk only (Q155, lane `fix-q154k`; the lane began 20:34 PST and this note was first written at
21:15 PST by the clock; its commit's own time is git's): no card was claimed, no device command was sent, no lab box or mini was reached,
nothing was posted. It sits beside [KIT.md](KIT.md) (the kit, `41865c18`) and its dated notes 1 (`6c158cd2`), 2 (`22da6a7b`) and 3
(`e0d31903`), which stay as committed, as do the registration ([E182.md](E182.md), `58b88850`), its notes 1 and 2 and every file of the five
hash lists (32, 79, 50, 49 and 89 OK after this note). It answers the adversarial verifier of note 3, E182.md's note 2 and the brief's note 1
(`verify-q154k`, 19:55-20:29 PST today: holds with fixes; 0 critical, 0 major, 2 minor, 3 nits): its fault 1, (a) in the brief's note 2,
(b) in step 6 v5, (c) in [E182.md.dated-note-3.md](E182.md.dated-note-3.md), and its nit 5 there; and critic-q154's nits 2 and 3 (Q154's
readiness critic, 19:14-19:49 PST), in the brief's note 2. It is committed before any E182 datum. **No forecast, threshold, statistic,
registered power figure, plan, cap or stop changes, no rule's reading changes, and no file the box session runs changes:** `harness-e182.json`
and `harness-e182-note1.json` are unchanged, and so is every box file step 5 v2 sends.*

## Results first

- **Step 6 v5** ([`rb/s08_a3_preflight_e182_v5.sh`](rb/s08_a3_preflight_e182_v5.sh) `start | wait | --no-trains`) is step 6 v4 with three fixes:
  - **a failed or cut wait call is not a failed build** (the verifier's fault 1; critic-q154's nit 2). k6's `rb_job_wait` returns 14 for a job
    that ended non-zero, for a lost job, and for a call that printed none of JOB-DONE, JOB-LOST or JOB-RUNNING. v4 read all three as a failed
    build, so a cut wait during the day's one re-run named the registered fallback. v5 reads a build's failure only from a whole
    `JOB-DONE a3-build-e182 rc=<n>` line with n non-zero, or from JOB-LOST. Any other 14 stops with **14**, "no reading of the build job ...:
    nothing is counted; run this step's wait again, and no other step-6 call (start or --no-trains) until it reads".
  - **`--no-trains` is refused after a good build that day** (10), as `start` is: "the registered fallback is for a failed build".
    v4's `--no-trains` passed beside a good train host.
  - **a cut check read is no reading** (found while fixing the first, the same kind). A check's read after the build, or one of the fallback's
    reads, that exits non-zero with no result line of its own is 14, "no reading of <check>: run this step's wait (or --no-trains) again".
    v4 counted it with the real failures and stopped 16, "a binary or file differs: a dated amendment first".
- **Step 2 v5** ([`rb/s03_desk_e182_v5.sh`](rb/s03_desk_e182_v5.sh)) checks six hash lists at pinned counts, **32, 79, 50, 49, 89 and 19**
  (this note's), and this note's desk test's log.
- **The fault, shown and fixed at the desk** ([`rb/selftest_rb_e182_v5.sh`](rb/selftest_rb_e182_v5.sh), **SELFTEST-RB-E182-V5 21 of 21
  PASS**, 249 s, on its first run). A stand-in ssh cuts the k-th remote script call (exit 255, nothing printed: verify-q154k's fail-once
  stand-in with a count):
  - N2v: step 6 v4, the first build failed, the re-run's wait cut: 16 naming the fallback, and v4's `--no-trains` passes (0) beside the good
    host. N2: step 6 v5 on the same sequence: 14 "no reading", the fallback not named; `--no-trains` refused while the job runs (10) and
    after the good build (10); wait reads the good build (0).
  - N4v and N4: the same with the re-run already ended good: v4 16 and `--no-trains` 0 at once; v5 14, `--no-trains` 10, wait 0.
  - N6v and N6: the first check's read cut after a good build: v4 16 "a dated amendment first"; v5 14 "no reading of inputs", then wait 0.
  - N1 and N1b (critic-q154's nit 2): a cut wait while the first build runs, or after it ended good: 14, nothing counted; wait 0; start 10.
  - R1-R4: with two REAL failed builds the fallback is named and runs as registered (a cut fallback read is 14, then `--no-trains` 0 and
    step 8 v2 `--no-trains` rc 0); L: JOB-LOST is still a build's failure (16, one re-run).
- **E182.md's dated note 3** ([E182.md.dated-note-3.md](E182.md.dated-note-3.md)) corrects four sentences of its note 2 (the verifier's fault 1
  (c) and nit 5): "a cut connection never did" end the trains was not true of step 6 v4 (it is of v5); E182.md section 3's sentence on the
  trigger reads as section 7's; a job lost before its start line is not counted; E180's 4 s box build was of another target. No rule's
  reading changes.
- **The brief's dated note 2** ([CARD-LANE-BRIEF.md.dated-note-2.md](CARD-LANE-BRIEF.md.dated-note-2.md)): after step 6's "no reading", wait
  again and no other step-6 call (with v4's case: after a 16 whose lines show "no reading (rc 14)" and no JOB-DONE or JOB-LOST line, wait
  again before ANY start or `--no-trains`, and never the fallback on that reading); E184's step 2 v2 does not itself refuse without the window,
  so each runbook's s02 runs first; E182's steps 2 and 6 are v5; E184 runs by its kit note 3.

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** KIT.md's block (INVENTORY.md read 13:30 PST) and notes 1-3's; this note re-read INVENTORY.md's rows H24 (the pool-8 card day,
   where the k6 runbook's drivers ran), H27 (E178's kit, whose form E182's is) and H28 (the kits' meter and stops) on Sat 7 Nov 2026 at 20:47
   PST. The row ids are opaque pointers into a private inventory. Newer pieces are cited by commit: E182's notes 1-3, E184's A4 (`a5f8ec1a`)
   and kit note 3 (`f9dcddac`).
2. **Used** (each unchanged, called, sourced, read or copied by path; sha256 in [`SHA256SUMS-e182-note4`](SHA256SUMS-e182-note4) or in
   note 3's list):
   - **Note 3's step 6 v4** (`rb/s08_a3_preflight_e182_v4.sh`): v5 is it, line for line, with the changes its header marks v5 (14 counted,
     exact replacements). **Note 3's step 2 v4** and **dry listing v4**: v5 of each is its predecessor with the stated changes.
   - **Note 3's desk test** (`rb/selftest_rb_e182_v4.sh`): its setup, copied into the v5 test with five stated changes (its header lists them);
     its stand-in cmakes and Q139(k)'s mock runtime, unchanged.
   - **The k6 runbook's drivers** (`rb_job_start`, `rb_job_wait`, `job_ok_today`, `jobs_live`, `ours_live`; v3.1's `rb_run.py`, which exits 14
     on any non-zero exit of its call) through `rb/rb_e182.sh`, unchanged.
   - **The verifier's own cases** (verify-q154k's `jobs/j2_e182_netfault.sh`, its N1, N1b, N2 and N4): run again here as the v5 test's cases,
     by this note's own code.
   - **E184's A4 and kit note 3**, read for the brief's note 2. *Check:* E184's step 2 v3 pins its eight lists at 11, 44, 6, 45, 3, 20, 1
     and 18, each reading that many entries, all OK (`logs/reruns-note4.txt`), and step 2 v3 ran for real at `f9dcddac`: rc 0.
3. **Not used:** rb_run.py's bound overrides; a change to k6's `rb_job_wait` (a shared driver four kits use: the reading is fixed in E182's own
   step instead); E180's code.
4. **Tiers:** every file of this note is public tier and cites public pieces only. No NDA-tier check enters it.
5. **Readiness:** this block is the note's. A verifier checks it against INVENTORY.md and the cited commits.

KIT.md's box steps are named by their numbers there (1 the window, 2 the desk check, 3 the post, 4 the look, 5 the sync, 6 the build and the
box's checks, 7 the reads, 8 the dry pass, 9 the session, 10 the wait, 11 the collection). The files are `rb/s02`, `s03`, k6's `s05`,
`s07`, `s08`, k6's `s09`, `s10`, `s11`, `s20` and `s22`.

## 1. Step 6 v5: a cut wait call is no reading, never a failed build (the verifier's fault 1)

**The fault** (the verifier's N2 and N4, reproduced here as N2v and N4v). `rb_job_wait` (k6's `rb_common.sh`, its line 364) prints "no reading
(rc 14)" and returns 14 when its call fails before the box prints JOB-DONE, JOB-LOST or JOB-RUNNING. Step 6 v4's wait (its lines 181-196) read
every 14 as a failed build, read the box's count, and at the day's second build stopped 16 with the fallback's words. Its `--no-trains` (its
lines 234-260) refused beside a session of ours or a running job, but not after a good build. So a dropped link during the one re-run's wait,
once that re-run had built well, led to the fallback beside a good train host: every train rule NOT SCORED on a network fault.

**The fix:**
- In wait's 14 branch, before anything is read as a build: unless the call's output holds a whole `JOB-DONE a3-build-e182 rc=<n>` line (n
  non-zero, since `rb_job_wait` returns 0 for n = 0) or a `JOB-LOST a3-build-e182` line, the step stops with 14 and names only the wait again.
  A truncated JOB-DONE line is no reading too. A real failed, overrun or lost build reads as in v4 (R1, R2, L).
- `--no-trains`'s first read carries a good-build refusal (the same test as start's: the job ended rc 0 today, its output reads
  TRAIN-HOST-BUILT, `build/e182host/SHA256` is there), before any check. The registered fallback (E182.md section 7, as note 2 reads it) is
  for two builds that did not read TRAIN-HOST-BUILT; a PASSES plan never needs step 6 `--no-trains` otherwise (step 9 v2's `PASSES no` accepts
  the trains' dry job too).

## 2. Step 6 v5: a cut check read is no reading (found by this lane, the same kind)

**The fault** (N6v). Each check after the build, and each of `--no-trains`' checks, runs in its own 60 s read whose remote script ends with
its own result line (`check_inputs_e182 rc=`, `check_e182 rc=`, `preflight_e182 rc=`, `e182_common rc=`), so it exits 0 whatever the
check reads. A non-zero exit with no result line is the call failing. v4's `check_read` ignored the call's status and collected the missing
result with the real failures: 16, "a binary or file differs: a dated amendment first". A card lane that followed those words would have
stopped E182 for the day on a network fault.

**The fix:** `check_read` takes the result line's pattern; a call that exits non-zero without it (and without NO-TREE, which stays a failed
check) is collected apart, and after the last check the step stops with 14, "no reading of <checks> ...: run this step's wait (or
--no-trains) again". Re-running wait reads all four checks again; a good host is never rebuilt (N6, R4).

## 3. Step 2 v5: note 4's list pinned

Step 2 v5 is v4 with a sixth list at its pin, `SHA256SUMS-e182-note4` 19, and this note's desk-test log checked as committed. The pins are
written in the file, with no override. Desk cases P1 and P2 cover it: on a scratch repository holding every listed file, with an origin so
that the pull runs, v5 passes the intact tree; with note 4's list one line short, v5 refuses (16): "SHA256SUMS-e182-note4(18 OK of 18; pinned
19)". Step 2 v4 passes the same tree, because it reads no note-4 list. Run for real on the committed tree after this note's commit, it reads 0.

## 4. Note 4's list

`SHA256SUMS-e182-note4` (19) holds this note's 12 other new files and the 7 E184 files the brief's note 2 cites (E184's A4 and kit note 3,
their two lists, step 2 v3, step 11 v3 and reduce v4), as note 3's list held E184's kit note 2 files its brief's note cited. Every other file
the new steps call, source or read is pinned by note 3's list (89), which step 2 v5 also checks.

## 5. The runbook as it now runs (KIT.md's box steps)

| KIT.md box step | file | changed here |
|---|---|---|
| 1, the window | `rb/s02_window_e182.sh` | no |
| 2, the desk check | **`rb/s03_desk_e182_v5.sh`** | v5 (section 3) |
| 4, the look, FIRST | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` | no (run before step 3: the brief) |
| 3, the post, after the look | (the card lane's) | no |
| 5, the sync | `rb/s07_a3_sync_e182_v2.sh` | no (note 1's v2) |
| 6, the build and the box's checks | **`rb/s08_a3_preflight_e182_v5.sh start`, then `wait`** while it says 17 or 14 (or `--no-trains`) | v5 (sections 1-2) |
| 7, the reads | `../q141k-runbook/k6/s09_a3_reads_k6.sh` | no |
| 8, the dry pass | `rb/s10_a3_dry_e182_v2.sh start|wait [--no-trains]` | no (note 1's v2) |
| 9, the session | `rb/s11_a3_session_e182_v2.sh FULL yes | PASSES no` | no (note 1's v2) |
| 10, the wait | `rb/s20_wait_e182.sh` | no |
| 11, the release, then the collection | `rb/s22_collect_e182_v3.sh` | no (note 3's v3) |

v1's steps 2, 5, 6, 8, 9 and 11, v2's steps 2, 6 and 11, v3's steps 2 and 6, and v4's steps 2 and 6 are not run on the card day. Step 6 v3 must
never run on a day step 6 v5 runs (it counts every line of the day in the count file). v5 reads the count file exactly as v4 does. The dry
listing of both paths is [`rb/list_steps_e182_v5.sh`](rb/list_steps_e182_v5.sh)
([`logs/dry-listing-e182-v5.txt`](logs/dry-listing-e182-v5.txt): 19 steps, 0 failing, the look listed before the post).

## 6. The checks, and what they re-ran

| check | result | log |
|---|---|---|
| the runbook v5 desk test (sections 1-3) | **SELFTEST-RB-E182-V5 21 of 21 PASS**, 249 s; step 6 v5's 148 calls in it, none past a bound, 6 of them cut by the stand-in, the longest read 0.7 s | `logs/selftest-rb-e182-v5.txt` |
| the dry listing v5, both paths | 19 steps listed, 0 failing, no call | `logs/dry-listing-e182-v5.txt` |
| dmcmd_audit, the runbook as it now runs with k6's steps 4 and 7 and the guard | GO, 11 send sites, every one READ: byte for byte note 3's runbook audit | `logs/dmcmd-audit-rb-v5.txt` |
| dmcmd_audit, this note's desk file | GO, 0 send sites | `logs/dmcmd-audit-note4.txt` |
| the harness check and the frozen lists, after this note; E184's eight lists at step 2 v3's pins | both makers CHECK PASS; HARNESS OK 66; NOTE1 FILES OK 10; 0 problems; registration 32/32, kit 79/79, note 1 50/50, note 2 49/49, note 3 89/89; no committed file edited since `e0d31903` in E182's paths, the workload or any path the five lists name; E184 11/11, 44/44, 6/6, 45/45, 3/3, 20/20, 1/1, 18/18 | `logs/reruns-note4.txt` |

The desk test's cases, in its own header: A, K, P1, P2, S1, X3, N1, N1b, N2, N2v, N4, N4v, N6, N6v, O, R1-R4, L and Z. On the stand-in box
the four box binaries are stand-ins that refuse if run, and the box's copy of `harness-e182.json` pins those stand-ins, as in notes 2's and
3's tests.

## 7. Labels

Every figure this note quotes from E182.md, its notes, the kit's notes and E184's kit (the caps, the plans, the stops, the pins) is
**registered**. The desk tests' results are checks of code at the desk, not measurements: nothing here is **blind** or **held out**, and no
E182 datum exists. E182.md's note 2 reading of the fallback's trigger stands unchanged.

## 8. For the verifier and the readiness critic

- The first real compile of the train host is still step 6 v5 on the box.
- Step 6 v5 adds no box-side write and no remote call to v4's: its changes are in how the desk reads the calls' outputs and status, plus one
  refusal (an `if` in the remote script) on `--no-trains`. It opens no device, and every remote call stays inside rb_run.py's bounds.
- k6's `rb_job_wait` still prints "no reading (rc 14)" and returns 14 to every kit that calls it. Step 8 v2's wait (`rb/s10_a3_dry_e182_v2.sh`)
  passes that 14 on as it is: there a second start re-runs a V3_DRY pass, which costs only time. The brief's note 2 says to wait again.
- The collector has still not run end to end on a raw tree (KIT.md open item 3).
- Card time waits on his word.

**Compute:** on the Intel through the round's slot, one job at a time, at nice 10: the runbook v5 desk test, the listing, the audits and the
re-runs. No bench job, mini, lab box or card was used. The tests wrote only under the round's scratch (their scratch git repository and
stand-in box).

SPDX-License-Identifier: Apache-2.0
