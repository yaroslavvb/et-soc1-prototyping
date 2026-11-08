# E183's run kit: six A B B A trains of one-number vector adds on aifoundry3 card 0 at 600 MHz, a host-only change that alternates two operand images launch by launch, the train host built on the box as one detached job, an exact copy-back, and the scorer for every registered rule (Q155; kitted, not run)

*Sat 7 Nov 2026 (week 45), PST, on the Intel, desk only (Q155, lane `e183`): no card was claimed, no device command was sent, no lab box was
reached, nothing was posted. New files only. The registration [`E183.md`](E183.md) (`c98a7287`, 20:47:49 PST, committed alone) and every
file its hash list names stay as committed (20 of 20 OK after this commit). This is the registration's section 12, step 2: the kit and the
scorer, in E182's v4 runbook form with its note 4's step 6 v5. No E183 datum exists. Nothing here changes a rule, a forecast, a threshold, a registered power figure, the
plan, a cap or a stop.*

**Labels.** Every forecast, rule, threshold and power figure the scorer reads is E183.md's, **registered** at `c98a7287` with the labels
it gives there: M10's P registered (E180's frozen), THE BLIND NUMBER **blind** (E180-L's measured price), the operand-bit arm and BOTH
**post hoc** (fitted on E180's committed reduction), the october-forecast-model's T5 frozen 6 Nov. The scorer's readings where E183.md leaves
a choice (the section below) are this kit's, **registered** with this commit, before any datum. The anchors, the carry-over, the joint fit
and the loop compare are **reported**, never verdicts. Nothing here is held out. Which of E180's commits each piece uses: the data commit
`c8a3a6ee` (its telemetry for the noise and the self-test's A1 and A2, its kernel listing for the loop compare, E180-L's price), the fix
`210d756e` (words only: nothing of it is read by code), the arm `b35fb232` (its reading of the october-forecast-model on E180's data:
cited, not read by code; the reader the forecasts call is dated note M2's `arm_m1_e180.py`, `2b32db9d`, on the model M1 froze, `b38d09e3`).

## Results first

- **The box kit, E180's form, for aifoundry3 card 0.** A train block (18310-18315) is one process of [`block_e183.sh`](block_e183.sh) (E180's
  block v2: lib.sh, D1's other-user rule, E128's telemetry guard, the drain refused, the 10 Hz sampler with no `--reset-ms`, the post-block
  check) running [`run_e183.py`](run_e183.py): a 10 s lead, the opening anchors (fadd.ps zeros, then random: E180's 3 s bursts after 4.5 s
  gaps), a 6 s gap, the train's processes back to back (52, or 202 for T5), each `timeout 10 <train host> --pattern fadd.ps --operands
  file:<F> --operands-b file:<S> --abba <ori> --launches 13 --harts 2 --seconds 30 --window 240000000`, then the closing anchors. E171's
  stops (65 W, 70 C on `minshire[0]`) are read before every burst and every process and every 0.1 s while one runs; D1's check runs before
  every burst and process. [`queue_e183.sh`](queue_e183.sh) runs FULL (18310-18315, cap 3,900 s from T0) or SHORT (18310 18311 18312 18314,
  cap 1,920 s) under E180's budget rule; [`session_e183.sh`](session_e183.sh) runs the harness check with the binaries, the device-command
  preflight, a config read through the guard, the stop-path test, the smoke and its gate, then the queue and a closing config read,
  **every file it writes named by its own T0** (E184 v2's rule).
- **The host-only change** ([`patch_host_e183.py`](patch_host_e183.py), applied by [`build_host_e183.sh`](build_host_e183.sh) to the copy of
  `host/main.cpp` in the build tree E180's own generator writes): `--operands-b`, `--abba SFFS|FSSF`, `--launches N`; the S image copied to
  the card once beside the F image, and each launch's `sources` pointed at one of them by the registered schedule; every ENERCAT line names
  its kind, image, orientation and launch number. The committed `main.cpp` (sha256 `3cad4adc...`) becomes the pinned `9b8f1a08...`.
  **Its desk test, DESKTEST-HOST-E183 PASS, 9 cases** ([`logs/desktest-host-e183.txt`](logs/desktest-host-e183.txt)): it compiles with no
  warning against E184's desk stubs and links with this kit's mock runtime ([`desk/mock_runtime_e183.cpp`](desk/mock_runtime_e183.cpp), E184's
  with one print a launch); trains SFFS and FSSF run 13 launches with each launch's own image (the mock's source word) and record; the
  refusals hold (no `--launches`, a bad orientation, a built-in fill, a short image); without `--operands-b` it is the catalogue's own loop;
  a train cut by the budget exits 3.
- **The box build, E182's step 6 form (v4, with its note 4's v5)** ([`rb/s08_a3_build_e183.sh`](rb/s08_a3_build_e183.sh)): one detached job under its own 500 s bound,
  refused beside a session of ours (k6's `ours_live`) or a runbook job (`jobs_live`), and after a good build that day; the build inputs at
  their pins before the job ([`check_inputs_e183.py`](check_inputs_e183.py): workloads/enercat's 37 committed files, E180's generator and its
  text, the patch), so an input off its pin reads TRAIN-HOST-INPUTS-DIFFER with step 5's words and no build is counted; inside the job a clean
  stage of the 37, E180's generator, the patch, and the whole tree against its pins (38 files) before cmake; at most one re-run of a failed,
  overrun or lost build, then **the registered fallback, SKIP** (E183.md section 7: no E183 session that day); each build's log and the day's
  count kept on the box and copied back. **E182's dated note 4 (its step 6 v5, `6b2d2ae6`, committed 21:16 PST tonight, after E183's
  registration) is ported in full:** a build's failure is read only from the box's own end of the job, a whole `JOB-DONE a3-build-e183
  rc=<n>` line or `JOB-LOST`, and any other 14 (a failed or cut wait call, critic-q154's nit 2 as verify-q154k widened it) stops with 14,
  "no reading: run this step's wait again", nothing counted or named; a cut read of a check after the build is no reading (14), never "a
  dated amendment first"; the fallback is never named beside a good train host.
- **The scorer** ([`score_e183.py`](score_e183.py), on [`reduce_e183.py`](reduce_e183.py)) reads every rule of E183.md section 5 with the
  registration's own statistics (`e183_stats.py`, imported unchanged). **Its self-test, SELFTEST-SCORE-E183 14 of 14 PASS**
  ([`logs/selftest-score-e183.txt`](logs/selftest-score-e183.txt)): on E180's committed data the reduction's launch reading gives
  noise-e183.json's 144 quads and sigma_q 0.06249 W to its five decimals (A1), and the anchors' reduction gives E180's RA5 on the board pass by pass to
  0.0 W (A2); synthetic sessions in the box's layout ([`fake_card_e183.py`](fake_card_e183.py)) read as their worlds (RESULT, OPERAND, BOTH,
  NEITHER), the noise at sigma_q and twice it reads TR-N and TR-H as registered, and a cut train, a bad launch, an orientation off the
  plan, the SHORT plan, an exponent control off the sum rule and a set-aside block each read as section 5 says.
- **The kernel's loop against E180's** ([`loopcmp_e183.py`](loopcmp_e183.py), reported): mode 160's loop found with E180's own walk in the
  box's listing and E180's committed one, compared instruction by instruction. **SELFTEST-LOOPCMP-E183 4 of 4 PASS**
  ([`logs/selftest-loopcmp-e183.txt`](logs/selftest-loopcmp-e183.txt)).
- **Device commands: `dmcmd_audit.py` GO, 32 send sites, 0 disallowed: every command E183 sends is a READ** ([`logs/dmcmd-audit-e183.txt`](logs/dmcmd-audit-e183.txt)):
  31 READ sites (E180's commands, through lib.sh and E128's guard) and one conditional STATS_RESET at lib.sh line 154, which E183 never
  reaches (its sampler call forwards no `--reset-ms`), EXCEPTED as E180's one reviewed exception (E153's, as E171's and E178's). The runbook's steps and the desk
  files send nothing of their own: the runbook's audit finds 11 sites, every one E128's guard (`ettelem_guard.sh`, through which k6's reads
  go) and every one READ ([`logs/dmcmd-audit-rb-e183.txt`](logs/dmcmd-audit-rb-e183.txt)); the desk files' audit finds 0
  ([`logs/dmcmd-audit-desk-e183.txt`](logs/dmcmd-audit-desk-e183.txt)).
- **The Intel dry pass, DRY-INTEL-E183 PASS, 25 of 25 checks** ([`logs/dry-intel-e183.txt`](logs/dry-intel-e183.txt)): the harness, the
  preflight, the dry build (the tree at its 38 pins), the guard, every train block of the plan (each block's processes in the plan's
  orientations through the train host), the smoke and the stop-path test, the refusals (an unplanned block, the smoke's number without
  `--smoke`, either card of aifoundry1), the queue's budget, deadline and plan rules, the session's start gates with their T0-named logs,
  a whole dry session, and no ssh, rsync or scp call.
- **The runbook** ([`rb/`](rb/)): E180's steps on k6's drivers, step 6 in E182's v4 form with v5's readings, step 11 with the exact copy-back. **Its desk test
  with a fake ssh and rsync, SELFTEST-RB-E183 17 of 17 PASS** ([`logs/selftest-rb-e183.txt`](logs/selftest-rb-e183.txt)): the 90 s stand-in
  build, E182 v5's network cut (the k-th remote call dropped: a cut wait at the first build and at its re-run, a cut check read) and a lost
  job among its cases. The dry listing: [`logs/dry-listing-e183.txt`](logs/dry-listing-e183.txt), 0 steps failing, the look before the post.

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** the stock-take's INVENTORY.md, read Sat 7 Nov 2026 about 20:20 PST (E183.md's block). Public rows read: L06, L11, L20, H21,
   H24, H27, H28, P11, P12. The row ids are opaque pointers into a private inventory. Pieces newer than it are cited by commit: E180's kit
   (`c92f627b`, notes `90a1312f`, `1e19a451`) and data (`c8a3a6ee`), E182's kit and notes (`41865c18`, `6c158cd2`, `22da6a7b`, `e0d31903`) and
   card-lane brief, E184's kit (`65f844be`, notes `eab0c70e`, `571511d0`); and, newer than E183's registration, **E182's dated note 4**
   (`6b2d2ae6`, 21:16 PST: step 6 v5 and its desk test, the brief's dated note 2).
2. **Used** (each unchanged, called, sourced or imported by path; its sha256 in [`harness-e183.json`](harness-e183.json) or
   [`SHA256SUMS-e183-kit`](SHA256SUMS-e183-kit)):
   - **E180's kit** (`tools/claims-v3/e180/`, which ran on aifoundry3 on 6 Nov 2026: the form of the block, runner, queue, session, checks,
     preflight, harness, collector, dry pass and runbook steps), and from it, unchanged: `gen_acc_e180.py` and `acc-modes-e180.inc` (the build
     tree), `others_d1_e180.sh` (D1's rule), `sync_paths_e180.py` (step 5's path list), `check_elf_e180.py` (the loop's walk), E180's images
     for 0.5, 1.5, 2, 4 and 5. *Check:* the dry build's tree equals the harness's 38 pins; the loop compare reads E180's own listing SAME.
   - **E182's step 6 v4 and v5 and their desk tests** (`tools/claims-v3/e182/rb/`: the detached build, its refusals, its count, its re-run
     rule; v5's three readings of a cut call; the stand-in cmakes, the fake ssh and v5's network cut and lost job): the form of
     `s08_a3_build_e183.sh`, `fake_cmake*_e183.sh` and `selftest_rb_e183.sh`; **E182's card-lane brief** and its dated note 2 (look before
     the post; one session of ours at a time; step 6 never beside a session of ours; each runbook's step 1 first; after a 14, wait again).
   - **E184's kit**: its desk stubs (`tools/claims-v3/e184/desk/stubs`, unchanged) and its mock runtime's form; its v2 rule that every file a
     session writes is named by its T0.
   - **The k6 runbook's drivers** (`q141k-runbook/k6/rb_common.sh`, its steps 5 and 9, v3.1's `rb_run.py` and `nopath_q142s.py`), sourced
     unchanged; **E178's `scrub_tree_e178.py`** (the login scrub); **Q136(w)'s `dmcmd_audit.py`**, **E128's guard**, **lib.sh**.
   - **The energy catalogue** (L06; `workloads/enercat`): its host, kernel and reduction (`analyze_catalogue.bursts_of`), unchanged.
   - **E183's registration** (`c98a7287`): `kinds-e183.json` and the images, `plan-e183.json`, `forecast-e183.json`, `noise/noise-e183.json` and
     `e183_stats.py`, each checked against the registration's list first (`e183_common.check_frozen`).
3. **Not used:** E182's sparsity host, C log and check of C (the vector add has no C to check; each launch's record names its image instead);
   E180's accumulating and integer modes (built in E180's tree, never run here); E184's enercat host change (its own); any other card.
4. **Tiers:** every file here is public tier and cites public pieces only. No NDA-tier check enters this kit.
5. **Readiness:** this block is the kit's. A verifier checks it against INVENTORY.md and the cited commits.

## E182's v4 runbook form, with note 4's step 6 v5, item by item

| E182's lesson | here |
|---|---|
| the box build as one detached job, each check after it in its own 60 s read | step 6 `start` launches `a3-build-e183` (k6's `rb_job_start`) under `timeout -k 15 500`; `wait` (k6's `rb_job_wait`, 17 while it runs) then four checks, each its own 60 s read |
| refused beside a session of ours or a runbook job | `ours_live` and `jobs_live` refusals before every start, `ours_live` before each check; k6's job start refuses beside a session too |
| no second build after a good one that day | refused (10) when job `a3-build-e183` ended rc 0 today with TRAIN-HOST-BUILT and BUILD-E183.json present |
| all build inputs checked before the job; an input off its pin is not a build | `check_inputs_e183.py` (40 pins) in the read before the job, and the tree (38 pins) inside it; TRAIN-HOST-INPUTS-DIFFER is never counted |
| at most one re-run, then the registered fallback | the box's own count file; after a second failed build, or at a third start: SKIP (E183.md section 7) |
| each build's log and the day's count reach the data | `build/e183-build-logs/<day>/e183-build-host-start<k>.txt` and `build/e183-build-attempts.txt`, copied back by step 11 |
| the look before the post; the window first | the dry listing lists k6's look before the post; step 2 refuses unless step 1 wrote today's window |
| a failed or cut wait call is not a failed build (critic-q154's nit 2; v5's fix 1) | step 6 `wait` reads a failure only from a whole `JOB-DONE a3-build-e183 rc=<n>` line or `JOB-LOST a3-build-e183`; any other 14 exits 14, "no reading of the build job: run this step's wait again", nothing counted or named (cases W and N2) |
| a cut read of a check is not a failed check (v5's fix 3) | each of the four checks' reads that exits non-zero without its own `... rc=` line (and no NO-TREE) is collected as no reading: 14, "run this step's wait again", before any 16 (case N6) |
| the fallback never beside a good host (v5's fix 2) | start is refused after a good build that day before the count is read, so no later wait can read a failed build and name SKIP (cases X3 and N2) |
| a lost job is a build's failure | JOB-LOST is read as one, counted, one re-run asked for (case L) |
| a slow stand-in build at the desk | `fake_cmake_slow_e183.sh` (90 s) in the runbook's desk test, case V, and the bound's case T |
| an exact copy-back | step 11 reads the box's own sha256 manifest of every file it copies; `copycheck_e183.py` reads COPY EXACT or step 11 stops (16) |
| T0-named session files | `session-t<T0>.log`, `queue-t<T0>.out`, `config-t<T0>-{start,end}.json`, `dmcmd-preflight-t<T0>.txt`; step 9 records T0 on the box and in RB_OUT; steps 10 and 11 read only that T0's files |
| the readers' interpreter pinned | every desk reader (the collector's reduction and scorer, the copy check, the login scrub, the self-tests) runs under `/usr/bin/python3` (3.9, with numpy for the anchors' reduction); the box runs its own `python3`, as E180's did |

## The scorer's readings, stated here before any datum (where E183.md leaves a choice)

- **A train process gives no value** when it has not exactly 13 launch records, when a record is not ok, when a launch's kind, orientation or
  number is off the plan's schedule, or when a stop fired during it (`stop.json` names it). A train with fewer than 8 units is NOT SCORED.
- **A block is set aside** when its `block.json` status is not ok or partial, or its files cannot be read; the rest are scored.
- **TR-N's pool:** every scored train's quads about their own train's and orientation's mean, one pooled sd over sigma_q (0.06249 W).
  **TR-H:** the median over the scored trains of the measured 95% half-width over the plan's `half_width_base_w`.
- **The anchors' reading** (reported): `analyze_catalogue.bursts_of` over each block's `runs.jsonl` (its four anchor bursts) and telemetry, a
  burst kept at 600 MHz; random - zeros at the block's open and at its close; the mean over blocks against E180's RA5 on the board.
- **The carry-over** (reported): per train, the mean of L3 - L2 over its SFFS quads less the same over its FSSF quads, over twice the train's
  estimate. **The joint fit** (reported): the scored trains on (dR, dO) through the origin, each weighted by 1 / se^2.
- **The owner's sentence for the add, measured:** E183-HT POSITIVE, its SIZE against BLIND PASS, and E183-MECH RESULT or BOTH.

## Card-minutes and the caps

| plan (`E183_PLAN`) | sequence | expected | cap (the budget rule) | the day's post says |
|---|---|---|---|---|
| **FULL** (default) | 18310-18315 (T3, T1, T4, T6, T2, T5) | **about 52** (plan-e183.json 51.9, plus the kit's 6 s gap before each train and the smoke's train, about 0.7) | **65** (3,900 s from E183_T0, 60 s reserve) | `for 1.5 h` |
| SHORT (chosen before the session when the window cannot fit FULL) | 18310 18311 18312 18314 (T3, T1, T4, T2) | about 26 | 32 (1,920 s) | `for 1 h` |
| the fallback, SKIP | no session | 0 | - | E183's clause dropped |

The queue projects a block at its plan estimate times the largest measured-to-planned ratio so far (1 until a block ends), plus 30 s. A
block in flight is never cut; nothing is skipped ahead.

## The order on aifoundry3

One session of ours at a time. E183 is not on the first card day (E182, then E184 arm S; E184 arm B on aifoundry1 card 1). It shares a later
day with E185 (M11's session 3): E185 first when its own gate wants the card at its morning floor, E183 after E185's step-11 copy-back; on a
day without E185, E183 may go first. E183's look, sync, build and dry pass start only after the previous run's copy-back has ended, and
step 6 refuses by code beside a session of ours or a runbook job. An idle login does not block (D1, the owner's ruling of 1 Nov 2026).

## The box steps that wait for the approvals and his go

Run them from the lab clone after `git pull --ff-only`, with this run's own `RB_OUT` (outside the repo) and the day's one `RB_LOCK`. The k6
drivers bound every remote call: a 15 s hard-killed probe, then 60 s for a read, 600 s for a copy. A printed login link stops the step (11)
and appends `<HH:MM:SS> aifoundry3 needs a check` to `RB_LOCK`.

| KIT.md box step | file | what |
|---|---|---|
| 1, the window (FIRST) | [`rb/s02_window_e183.sh`](rb/s02_window_e183.sh) `<day> <last start> <last end>` | his go's window, PST |
| 2, the desk check | [`rb/s03_desk_e183.sh`](rb/s03_desk_e183.sh) | the window written today; pull; HEAD descends from `c98a7287`; E183's paths clean; the registration's list (20) and the kit's (46) at their pins; the harness rebuilt; the registration verified; HARNESS OK 80; BUILD INPUTS OK 40; the four desk tests' logs |
| 4, the look (BEFORE the post) | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` | k6's, unchanged |
| 3, the post | the card lane's, under the post's lock | `using aifoundry3 for 1.5 h, until ~HH:MM PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)` (`for 1 h` for SHORT) |
| 5, the sync | [`rb/s07_a3_sync_e183.sh`](rb/s07_a3_sync_e183.sh) | every harness file and the harness, one rsync |
| 6, the train host's build | [`rb/s08_a3_build_e183.sh`](rb/s08_a3_build_e183.sh) `start`, then `wait` while it says 17 | one detached job; the re-run rule; the fallback SKIP |
| 7, the reads | `../q141k-runbook/k6/s09_a3_reads_k6.sh` | k6's, unchanged |
| 8, a V3_DRY pass on the box | [`rb/s10_a3_dry_e183.sh`](rb/s10_a3_dry_e183.sh) `start`, then `wait` while it says 17 | block 18310, the smoke, the stop test, the start gate (8) |
| 9, the session | [`rb/s11_a3_session_e183.sh`](rb/s11_a3_session_e183.sh) `FULL` (or `SHORT`) | today's good build and dry pass; T0 recorded; launched detached |
| 10, the wait | [`rb/s20_wait_e183.sh`](rb/s20_wait_e183.sh), again while it says 17 | that T0's log, to its "session end (T0 ...)" |
| 11, release, then collect | the post's release; then [`rb/s22_collect_e183.sh`](rb/s22_collect_e183.sh) | the exact copy-back, `collect_e183.sh`, the desk-path gate, the login scrub |

[`rb/list_steps_e183.sh`](rb/list_steps_e183.sh) is the dry listing of this table. After step 11 the data directory is
`docs/reports/data/<day>-e183-vector-add-r2-aifoundry3/`; its public-text scan, the data commit's message with it, comes before its commit.

## Files, and what each builds on

| file | what | builds on |
|---|---|---|
| `e183_common.py` | the registration's kinds, trains, plan and images, the schedule, each run's host arguments, the frozen checks | `e182_common.py`'s form |
| `patch_host_e183.py`, `build_host_e183.sh`, `check_inputs_e183.py` | the host-only change, its box build, its pins | `patch_host_e182.py`, `build_e180.sh`, `check_inputs_e182.py` |
| `run_e183.py`, `block_e183.sh`, `queue_e183.sh`, `session_e183.sh` | the runner, a block, the plan's budget, the session | E180's v2 four, `run_e182t.py` |
| `check_e183.py`, `preflight_e183.sh` | the harness check, the post-block check and the smoke gate; the device-command preflight | E180's `check_e180_v2.py`, `preflight_e180_v2.sh` |
| `harness-e183.json`, `make_harness_e183.py` | the sha256 of the box's 80 files, the 40 build inputs and the 38-file build tree | `make_harness_e180_v2.py` |
| `reduce_e183.py`, `score_e183.py`, `collect_e183.sh`, `copycheck_e183.py`, `loopcmp_e183.py` | the reduction, every rule, the collection, the exact copy-back's check, the loop compare | E180's v3 reduction and collector; E182's scorer forms |
| `selftest_score_e183.py`, `fake_card_e183.py` | the scorer's self-test on E180's committed data and synthetic sessions | E182's self-test forms |
| `desk/desktest_host_e183.sh`, `desk/mock_runtime_e183.cpp` | the train host against the mock runtime | E184's desk test and mock |
| `dry_intel_e183.sh` | the Intel dry pass with stand-in ssh, rsync and scp | `dry_intel_e180_v2.sh` |
| `rb/` | steps 1, 2, 5, 6, 8, 9, 10, 11, the dry listing, the desk test with a fake ssh and rsync, the stand-in cmakes | E180's runbook on k6's drivers; E182's step 6 v4 and v5 and their desk tests |
| `logs/` | every check above | |
| `SHA256SUMS-e183-kit` | the kit's 46 files (this file, the code, the harness and the logs) | |

## Open items (for the verifier, the readiness critic and the records)

1. A verifier of this commit, then a readiness critic; card time only on his go, with fresh network approvals.
2. **The train host's first compile is on the box** (step 6): the desk compiles the patched `main.cpp` only against the mock runtime. A failed
   build gets one re-run; after a second, SKIP (no card time spent).
3. **The collector has not run on a real session's raw tree** (its reduction and scorer have, on E180's committed bursts and on synthetic
   sessions in the box's layout; step 11's copies and their check have, on a stand-in box). Its first full run is the card day's step 11.
4. **The october-forecast-model** (E183.md section 8): its committed reader (E180's `arm_m1_e180.py`, dated note M2 `2b32db9d`, on the
   model frozen Fri 6 Nov in dated note M1 `b38d09e3`) covers his pair alone, so the scorer reads OFM as one SIZE word on T5 (E183-HT) and nothing else; reported.
5. **The kernel's listing** needs `/opt/et`'s objdump on the box (E180's box had it); without it the loop compare reads UNREAD (reported).
6. Card 1 is not kitted.
7. **E180's recorded nits 7-9 stand for the box files E183 uses as E180 did** (E180's kit note 2, section 5): D1's `others_d1_e180.sh`
   reads `$USER` (the planned route sets it: step 9 launches over ssh and the session inherits the login's environment); the check before
   every burst and process calls the box's holder reader (`et-holders`, as E180's did), a read, about 490 times in a FULL session (E180's about 290), its
   time inside the plan's 0.199 s a run (E180's measured); the harness checks that `build/ettelem/ettelem` is executable but does not pin
   it, as E180's did not.

## Compute

On the Intel through the round's local slot (`slot.sh`), one job at a time, at nice 10: the patch's desk test (about 5 s: one generated
tree, two compiles, eight short runs), the harness (seconds), the audits (seconds), the scorer's self-test (about 40 s), the loop compare's
self-test (seconds), the Intel dry pass (about 50 s) and the runbook's desk test (3 min 55 s, its 90 s stand-in build among it). No bench job, mini,
lab box or card was used. The desk tests wrote only under the round's scratch.

SPDX-License-Identifier: Apache-2.0
