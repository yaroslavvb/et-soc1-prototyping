# E180's run kit: the one-number vector adds on aifoundry3 card 0 at 600 MHz, 47 runs a pass in the plan's order with the energy catalogue's timing and E171's live stops, and the scorer for every registered rule (Q146(f); kitted, not run)

*Fri 6 Nov 2026 (week 45), about 01:00-01:50 PST, on the Intel, desk only (Q146(f), lane `add-q146f`): no card was claimed, no device
command was sent, no lab box was reached, no archive was read, nothing was posted. New files only: the registration [`E180.md`](E180.md) (`4dc5035f`,
01:22:09 PST) and every file [`SHA256SUMS-e180-registration`](SHA256SUMS-e180-registration) lists stay as committed (71 of 71 OK after this
commit). This is section 12's step 3, the kit and the scorer. No E180 datum exists: `git log --all` shows no `docs/reports/data/*e180*`.
It answers the owner's ask of Thu 5 Nov 2026, about 19:30 PST ("maybe even adding, like adding a matrix filled with 4s is a different
than adding a matrix filled with 5s"), for the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 6. Nothing here changes a rule, a
forecast, a threshold or a registered power figure.*

## Results first

- **The box kit, in V3-CATFULL's form** (`tools/claims-v3/catfull/block.sh`: lib.sh's look, preflight, block_begin, code hashes, the clock,
  the sampler, the runner, the post-block check, gzip, block_end) with E180's runner [`run_e180.py`](run_e180.py): the catalogue runner's
  protocol (`tools/claims-v3/cat/run_catalogue_t10.py`: `timeout 10` on every device process, the 3 s burst of 0.4 s launches, the 4.5 s
  gap, the 10 s lead, `others_present` before every run, the stalled-sampler stop) with E180's 47 configurations in plan-e180.json's
  order and E171's live stops (65 W, 70 C on `minshire[0]`, before every run and every 0.1 s during it). FULL (18010-18015, cap 50
  card-minutes) and TWO (18010-18011, cap 20); the stop-path test 18002 (no launch: the board and the die stop must each fire before a run
  and in the in-run watcher, on live samples) and the smoke 18001 (four runs, 1 s bursts) gated by `check_e180.py smoke`.
- **The build:** [`build_e180.sh`](build_e180.sh), a box step before the session, copies the committed `workloads/enercat` into
  `build/enercat-e180-src`, appends the two accumulating modes (`gen_acc_e180.py`; its appended text must equal the registration's
  `acc-modes-e180.inc`), builds with the box's own toolchain at nice with 4 jobs, and records the host's and kernel's sha256 in
  `build/enercat-e180/BUILD-E180.json`, which the session's harness check compares before any device opens. Every E180 run uses this
  one build.
- **The scorer** ([`score_e180.py`](score_e180.py)) reads every rule of E180.md section 5 with `power_e180.py`'s own statistics
  (imported unchanged): H, L, O, R, E, I, X and A, P scored and C, E, F and A's SIZE beside, and the owner's sentence for the add only
  when H reads POSITIVE with SIZE PASS, P's slope is inside L and O reads NULL.
  - **Its self-test, 12 of 12 PASS** ([`logs/selftest-score-e180.txt`](logs/selftest-score-e180.txt)). Synthetic sessions read as
    designed: P true reads every rule as registered and the sentence measured; C, E, F and A true each put L inside that arm alone (and
    H's SIZE FAIL LOW or HIGH); an operand-bit term reads O POSITIVE; fadd.pi's write-back returning to zero reads I POSITIVE; no
    difference reads H NOT RESOLVED and R FAIL; one kept pass gives NOT SCORED; card 1's forecasts and a set-aside pass are handled.
    Two raw passes (10 Hz telemetry with idle brackets, runs in the host's ENERCAT form) go through `reduce_e180.py` and
    `analyze_catalogue.bursts_of` unchanged and give each kind's D back (mean error 0.013 W at 0.05 W of noise a sample).
- **Device commands: `dmcmd_audit.py` GO, 32 send sites, 0 disallowed, every one READ** ([`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt)).
  E153's one reviewed exception, `lib.sh:154`, is E171's and E178's: the statistics reset is never sent. Without it the audit reads NO-GO
  exactly there ([`logs/dmcmd-audit-noexcept.txt`](logs/dmcmd-audit-noexcept.txt)). The desk files send nothing (GO, 0 sites,
  [`logs/dmcmd-audit-desk.txt`](logs/dmcmd-audit-desk.txt)). The runbook's steps with k6's steps 5 and 9 read GO, 11 sites, all E128's
  guard lines ([`logs/dmcmd-audit-rb.txt`](logs/dmcmd-audit-rb.txt)). The enercat host opens the card through the runtime only.
- **The Intel dry pass, DRY-INTEL PASS, 23 of 23 checks** ([`logs/dry-intel.txt`](logs/dry-intel.txt)), with stub binaries that refuse if
  run and stand-in ssh, rsync and scp that log and refuse: the harness, the audit and the dry build; every planned pass 47 runs through the
  E180 host in plan-e180.json's order (the runner's own record, `configs.json`, equals the plan run for run); the smoke 4; the stop-path test
  both stops; an unplanned pass, the smoke's number without `--smoke` and aifoundry1's card 0 refused before any device call; the queue's
  budget, deadline and plan rules; the session's three start gates; a whole dry session (stop-path test, smoke, six dry passes) that writes
  `session-dry.log` and never the real session's log; no network call.
- **The runbook (the k6 v3 drivers, sourced unchanged), desk test 14 of 14 PASS with a fake ssh and rsync**
  ([`logs/selftest-rb-e180.txt`](logs/selftest-rb-e180.txt)): the dry listing, a login link (11 and its lock line), a silent probe (12), a
  launch past its bound (13), a failed smoke gate read at the end (16), no window (10), past the last start (16), no dry pass or build
  ended today (refused on the box, 10), no launch offset (10), a good collection (0), a stop-path test with a launch (14), a desk path in
  the output (16), no success line (14), the collector stand-in without its flag (10). Its dry listing
  ([`logs/dry-listing-e180.txt`](logs/dry-listing-e180.txt)) makes no network call.
- **The harness:** [`harness-e180.json`](harness-e180.json), 56 files (E180's box files, the registration's files the box reads, lib.sh,
  E128's guard, the checker and its table, and the committed `workloads/enercat` the build copies, file by file); lib.sh equals the one
  E171 ran and E178 kits. `check_e180.py harness`: HARNESS OK, 81 files with the 25 images ([`logs/harness-check.txt`](logs/harness-check.txt)).
- **The registration re-makes**: `power_e180.py --check` byte for byte ([`logs/power-check.txt`](logs/power-check.txt)), beside the faster
  checks of E180.md section 13.

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** the stock-take's INVENTORY.md and MAP.md, read Thu 5 Nov 2026 about 23:45-23:55 PST. Public rows read: H09, H21, H24, H27,
   H28, L06, L20, L21, P05, P06, P07, P12, P13; MAP rows 5, 6, 41 and section 3. The row ids are opaque pointers into a private file.
2. **Used** (each unchanged, called or sourced by path, its sha256 in [`SHA256SUMS-e180-kit`](SHA256SUMS-e180-kit) or `harness-e180.json`):
   - **V3-CATFULL** (`tools/claims-v3/catfull/`, the 25-26 Sep four-card catalogue): the block's form; **V3-CAT's runner**
     (`tools/claims-v3/cat/run_catalogue_t10.py`): the runner's protocol, which `run_e180.py` keeps line for line where E180 does not
     change it (its docstring lists the five changes). *Check:* catfull measured 8.0 s a configuration; the plan's 8.1 s a run and 43
     card-minutes for FULL rest on it.
   - **The energy catalogue's reduction** (`workloads/enercat/analyze_catalogue.py`, `bursts_of` and its leakage correction), imported
     unchanged by the post-block check and the reducer. *Check:* S9-S10 of the scorer's self-test.
   - **E178's kit** (`tools/claims-v3/e178/`, `a4aafc6f` and its notes): the form of the session, the queue, the preflight, the harness
     maker, the dry pass and every runbook step; its SIZE words (dated note A2, `c212a345`).
   - **E171's stops** (`tools/claims-v3/e171/run_e171.py`, E163's values) and **the kits' meter** (`tools/ettelem`, lib.sh): the live
     stops and the sampler.
   - **The k6 runbook's v3 drivers** (`q141k-runbook/k6/rb_common.sh`; v3.1's `rb_run.py`, `nopath_q142s.py`), sourced unchanged; k6's
     steps 5 and 9 used unchanged. **E164's login scrub** (`e164/scrub_etwho_e164.py`) in `--check` form at the collection.
   - **Q136(w)'s `dmcmd_audit.py` and table, and E128's `ettelem_guard.sh`**: the audits and the config reads.
   - **E180's registration** (`kinds-e180.json` and the images, `cfgs-e180.json`, `plan-e180.json`, `forecast-e180.json`, `power_e180.py`):
     imported unchanged, each in the registration's hash list.
3. **Not used:** E178's check of C (the catalogue's host keeps no C log; not applicable); the catfull preheat and clock-drop rule
   (aifoundry3 is pinned at 600 MHz; catfull itself runs none there); E172's card-1 kit (owed, only if aifoundry3 is held: see open items).
4. **Tiers:** every file here is public tier and cites public pieces only. No NDA-tier check enters this kit.
5. **Readiness:** this block is the kit's. A verifier checks it against INVENTORY.md and the cited commits.

## The scorer's readings, stated here before any datum (where E180.md section 5 leaves a choice)

- **A kind's per-pass D** is the mean over_idle_w of its kept bursts in the pass (`reduce_e180.py`: a burst is kept when every busy
  sample read 600 MHz); a repeat (`@r2`, `@r3`) is averaged with its kind. A pass is kept when its block reads ok or partial and every
  kind has a kept burst in it, else it is set aside with the reason, and the rules read the kept passes only.
- **E180-L's line** is the scored card's own P slope (on aifoundry3 the registration's 0.1649 W a bit; on card 1 0.1584, from card 1's
  frozen P). Each arm's slope is the same OLS over that card's forecasts.
- **E180-E's 95% point** is drawn from the measured members' se (sd over passes / sqrt n), 20,000 draws from `random.Random(18004)`.
- **SIZE words:** FAIL HIGH means the forecast is above the measured interval (the model prices more than the card reads), FAIL LOW below
  (E178's words as its dated note A2 settles them). Every SIZE verdict is printed in words.
- **Reported, never a verdict:** every kind's D above its zeros against P, C, E, F and A, its sd and its measured instruction rate.

## Card-minutes and the cap

| plan (`E180_PLAN`) | sequence | expected | cap (the budget rule) | the day's post says |
|---|---|---|---|---|
| **FULL** (default) | 18010-18015 | **about 43** | **50** (3,000 s from E180_T0, 60 s reserve) | `for 1.5 h` |
| TWO (the registered subset) | 18010, 18011 | about 15 | 20 (1,200 s) | `for 1 h` |

The queue's first estimate is 420 s a pass, then the longest measured. A pass in flight is never cut, and a seventh is never planned. Box
steps before the session (look, sync, the build about 2 min, preflight, reads, the dry pass) add about 25-35 minutes of wall time.

## The order on aifoundry3

E180 runs alone on aifoundry3, starting with `et-who` clean; an idle login does not block (D1, the owner's ruling of 1 Nov 2026). Never two
of our sessions on one card. The build runs only after the look reads FREE and never beside a session of ours (k6's job rule refuses it).
If M11's next hold session or E178 runs on aifoundry3 the same day, E180 goes after them or on another day: its passes warm the card.

## The box steps that wait for the approvals and his go

Run them from the lab clone after `git pull --ff-only`, each with this card day's `RB_OUT` and `RB_LOCK`. The k6 drivers bound every remote
call: a 15 s hard-killed probe, then 60 s for a read or a launch, 600 s for a copy or a wait. A printed login link stops the step (11) and
appends `<HH:MM:SS> aifoundry3 needs a check` to `RB_LOCK`.

1. **His go and fresh network approvals** for aifoundry3, with the round's time gates. Then [`rb/s02_window_e180.sh`](rb/s02_window_e180.sh)
   `<day> <last start> <last end>`.
2. **The desk check**, [`rb/s03_desk_e180.sh`](rb/s03_desk_e180.sh): pull; HEAD descends from `4dc5035f`; E180's paths clean; the two hash
   lists; the harness rebuilt; the plan and the forecasts re-made; HARNESS OK without binaries. It reports any october-forecast-model
   freeze note and any E180 data in any ref.
3. **The day's one post** in `#community-lab` (the card lane's, under the post's lock):
   `using aifoundry3 for 1.5 h, until ~HH:MM PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`.
4. **Look first:** `../q141k-runbook/k6/s05_look_k6.sh aifoundry3 [--wait]` (k6's, unchanged).
5. **Sync:** [`rb/s07_a3_sync_e180.sh`](rb/s07_a3_sync_e180.sh), one rsync of E180's directory and the committed `workloads/enercat`;
   uncommitted changes refuse.
6. **The build and the checks on the box:** [`rb/s08_a3_build_e180.sh`](rb/s08_a3_build_e180.sh) `start`, then `wait` while it says 17:
   `build_e180.sh`, HARNESS OK with the binaries, the preflight GO. If a recorded binary differs, stop: a dated amendment registers it first.
7. **Reads:** `../q141k-runbook/k6/s09_a3_reads_k6.sh` (k6's, unchanged): `et-lab-manifest`, the config through the guard (0 W / 65 C /
   600 MHz), et-who clean.
8. **A V3_DRY pass on the box:** [`rb/s10_a3_dry_e180.sh`](rb/s10_a3_dry_e180.sh) `start`, then `wait` while it says 17: pass 18010's 47
   runs, the smoke's 4, the stop-path test and the start gate refusing (8). It writes the dry session's own log only.
9. **The session:** [`rb/s11_a3_session_e180.sh`](rb/s11_a3_session_e180.sh) `FULL` (or `TWO`). It launches
   `E180_T0=$(date +%s) E180_PLAN=FULL E180_LATEST_START=<last start> E180_DEADLINE=<last end> setsid nohup bash tools/claims-v3/e180/session_e180.sh`
   detached, only when the dry pass and the build ended rc 0 today. The session runs the harness with the binaries, the preflight, the
   stop-path test and the smoke with its gate before any pass.
10. **Wait:** [`rb/s20_wait_e180.sh`](rb/s20_wait_e180.sh), repeated while it says 17.
11. **Release, then collect:** the post's release. Then [`rb/s22_collect_e180.sh`](rb/s22_collect_e180.sh): the copies into
    `build/e180-raw`, the stop-path test checked to have launched nothing, `collect_e180.sh` (`reduce_e180.py`, `score_e180.py`), E164's
    scrub check and the desk-path gate. The output is `build/e180-out/<day>-e180-vector-add-aifoundry3/`, and the data directory is
    `docs/reports/data/<day>-e180-vector-add-aifoundry3/`. The login scrub and the public-text scan come before its commit; then a data
    verifier and a fix pass.

## Files, and what each builds on

| file | what | builds on |
|---|---|---|
| `run_e180.py` | the runner: E180's configurations in the plan's order, the catalogue's timing, E171's live stops, the stop-path test | `cat/run_catalogue_t10.py`; `e171/run_e171.py` |
| `block_e180.sh` | one pass, the smoke or the stop-path test on the local card | `catfull/block.sh` |
| `queue_e180.sh`, `session_e180.sh` | the plan's budget; the session with its gates | E178's two |
| `check_e180.py` | the harness check, the post-block check, the smoke gate | `catfull/cflib.py` check; E178's check |
| `preflight_e180.sh` | the device-command preflight | E178's |
| `build_e180.sh` | the box build of the catalogue with the two accumulating modes | `gen_acc_e180.py` (the registration's) |
| `make_harness_e180.py`, `harness-e180.json` | the sha256 of everything the box runs or builds from | E178's harness maker |
| `reduce_e180.py`, `collect_e180.sh` | each kind's D per pass from `bursts_of`; the desk collection | `analyze_catalogue.py`; catfull's reduce |
| `score_e180.py`, `selftest_score_e180.py` | section 5's rules; their self-test | `power_e180.py`'s statistics |
| `dry_intel_e180.sh` | the Intel dry pass with stand-in ssh, rsync and scp | E178's |
| `rb/` | steps 2, 3, 7, 8, 10, 11, 20, 22, the dry listing, the desk test | the k6 runbook (v3 drivers); E178's steps |
| `logs/` | every check above, and the four audits | |
| `SHA256SUMS-e180-kit` | the kit's files, its logs and the unchanged files it calls | |

## Open items (for the verifier, the readiness critic and the records)

1. A verifier of this commit, then a readiness critic. Card time only on his go and fresh approvals.
2. **The box build is new.** The E180 build has never been compiled on a box: step 6 is the first time the ET toolchain assembles the two
   appended cases (`fxor.pi` and `fadd.ps` / `fadd.pi` with a sink as a source, forms the toolchain already assembles in other modes). If
   it fails, E180 does not run that day; the fix is a dated amendment. The smoke's gate (rates equal within 3% across fadd.ps, the
   accumulating fadd.ps and fadd.pi) is its first functional reading; nothing in the host checks the sums' values.
3. aifoundry1 card 1, the registered fallback (E180.md section 7; its forecasts are frozen), is not kitted beyond `block_e180.sh`'s
   `V3_DEVICE=1` path. If aifoundry3 is held at the go, E180 waits; card 1 needs its own runbook port and readiness check.
4. The october-forecast-model freeze (E180.md section 8) is not committed; without it before the first launch, that forecast is not scored.
5. If the anatomy (CONTEXT section 43) wants readings E180 does not take (an idle read beside each pass, say), a dated amendment before
   any datum.

## Compute

All on the Intel, desk only. The kit's files were drafted in the lane's scratch from about 01:00 PST, while the registration's power
simulation ran, and copied into the clone only after the registration's commit `4dc5035f` (01:22:09 PST); none of them is read by any
registered file, and no registered file changed. Through the round's local slot (`slot.sh`), one job at a time at nice 10, one core: the
scorer's self-test (2 s) and `power_e180.py --check` (about 8 min). Outside the slot, each under a minute: the harness maker, the four
audits, the dry pass (37-46 s, three runs: the first stopped at bash 3.2's empty-array rule, fixed before the second; the third, the
logged one, after the public-text scan reworded two comment lines, one in `run_e180.py`'s docstring, so the harness was re-made and its
check, the preflight and the dry pass re-run; every check read as before, and the preflight's log is byte for byte the same), the
runbook's desk test (12 s) and dry listing. No bench job, mini, lab box or card was used for the kit. The dry pass and the desk test ran
in the lane's scratch, never in the lab clone.

SPDX-License-Identifier: Apache-2.0
