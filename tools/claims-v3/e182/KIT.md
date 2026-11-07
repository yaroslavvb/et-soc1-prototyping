# E182's run kit: six A B B A trains and E178's kinds passes on aifoundry3 card 0 at 600 MHz, a host-only change that alternates two kinds launch by launch, every launch's C checked against its own tiles, and the scorer for every registered rule (Q153; kitted, not run)

*Sat 7 Nov 2026 (week 45), PST, on the Intel, desk only (Q153, lane `e182`): no card was claimed, no device command was sent, no lab box was reached,
nothing was posted. New files only. The registration [`E182.md`](E182.md) (`58b88850`, 13:57:12 PST) and every file its
hash list names stay as committed (32 of 32 OK after this commit). This is the registration's section 12, step 2: the kit and the scorer. No
E182 datum exists. It answers the owner's ask of Thu 5 Nov 2026, about 19:30 PST ("here's a matrix filled with one number, and here's a
matrix filled with another number, and they require different number of transistor flips, therefore they will use different power"), a
second time, for the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 6.
Nothing here changes a rule, a forecast, a threshold or a registered power figure.*

## Results first

- **The box kit, E178's form, for aifoundry3 card 0.** The kinds passes 18220-18223 are E178's: E78's runner and reduction unchanged, with
  E182's 24 kinds and its registered order installed (`e182_common.py`), every launch through Q139(k)'s C-logging wrapper, E171's live stops
  (65 W, 70 C on `minshire[0]`) and in-run watcher. **The trains** 18210-18215 are new: each block runs its format's zeros and random
  anchor as E78 runs, then the pair's 64 (int8) or 76 (fp32) processes back to back through `run_e182t.py`, then the anchors reversed; one
  sampler and one C log for the block. FULL (the six trains in the plan's order, then three or four kinds passes; cap 100 card-minutes) and
  PASSES (three kinds passes, the trains' registered fallback; cap 40); the stop-path test 18202 and the smoke 18201 (ten kinds items, then
  two processes of T1's train) gated as E178's, with a second gate for the train part.
- **The host-only change** ([`patch_host_e182.py`](patch_host_e182.py), built on the box by [`build_host_e182.sh`](build_host_e182.sh)): Q139(k)'s
  C-log patch applied unchanged, then `--values-b`, `--abba SFFS|FSSF` and `--launches N`. **Its desk test, DESKTEST-HOST-E182 25 of 25 PASS**
  ([`logs/desktest-host-e182.txt`](logs/desktest-host-e182.txt)): built against the check of C's mock runtime, five trains (T1 both
  orientations, T2, T5, T6) print 14 records each with every launch's kind by the registered schedule; the C log holds both tile sets once
  and pairs every launch's C with its own tiles; ccheck.py judges all 70 train launches PASS; both tile sets dump byte for byte; the
  three refusals hold (no `--launches`, a bad orientation, a built-in `--values`); without `--values-b` it is the C-logging host; and a C
  record re-paired to the other kind's tiles FAILs exactly that launch. The registered patched source's sha256 is in `harness-e182.json`.
- **The scorer** ([`score_e182.py`](score_e182.py), on [`reduce_e182.py`](reduce_e182.py)'s two reductions) reads every rule of E182.md
  section 5 with the registration's own statistics (`e182_stats.py`, imported unchanged). **Its self-test, SELFTEST-SCORE-E182 12 of 12
  PASS** ([`logs/selftest-score-e182.txt`](logs/selftest-score-e182.txt)): on E178's committed data the slope rule gives E178-W-int8's committed
  2.7812 fJ a flip exactly (its interval to E178's rounded t), Spearman gives E178-R-int8's rho exactly, and the train functions on E178's
  telemetry give `noise-e182.json`'s quad sd exactly; synthetic sessions in the box's layout ([`fake_card_e182.py`](fake_card_e182.py)) read
  as their truths (B-ONLY, A+B, P's world, noise at 2.5 times, a train cut short, a C FAIL, one kinds pass), an arm reads as the primary does,
  the C-session list is right,
  and the smoke gate's train part passes a good smoke and fails a launch off the schedule.
- **Device commands: `dmcmd_audit.py` GO, 32 send sites, 0 disallowed, every one READ** ([`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt)): the
  same commands as E178. Without E153's one reviewed exception (`lib.sh:154`) the audit reads NO-GO exactly there
  ([`logs/dmcmd-audit-noexcept.txt`](logs/dmcmd-audit-noexcept.txt)). The desk files and the runbook's steps send nothing of their own
  ([`logs/dmcmd-audit-desk.txt`](logs/dmcmd-audit-desk.txt), [`logs/dmcmd-audit-rb.txt`](logs/dmcmd-audit-rb.txt)).
- **The Intel dry pass, DRY-INTEL PASS, 29 of 29 checks** ([`logs/dry-intel.txt`](logs/dry-intel.txt)): every planned kinds pass (70 launches through the wrapper,
  the order run_e78 ran equal to `plan-e182.json`), every train (four anchors, then every planned process with its F and S tiles, the
  planned orientation and `--launches 13`), the smoke (10 and 2), the smoke with the trains off, the refusals, the queue's budget,
  deadline, plan and train-projection rules, FULL's and PASSES' sequences, the session's four start gates, and no ssh, rsync or scp call.
- **The runbook** ([`rb/`](rb/)): E178's v2 steps ported, with the train host's first compile on the box at step 6. **Its desk test with a
  fake ssh and rsync, SELFTEST-RB-E182 9 of 9 PASS** ([`logs/selftest-rb-e182.txt`](logs/selftest-rb-e182.txt)): the dry listing makes no call; step 3
  refuses without step 2's window (kit v5); step 7 on a clean stand-in box builds a tree that holds every non-built harness file at its
  sha256, where the box's own checks pass in V3_DRY (HARNESS OK 66, GO, 0 problems, the three dry blocks, the start gate) with no network
  call (the E174 class); step 7 refuses an uncommitted harness file; steps 11, 20 and 22 refuse as they should. The dry listing, 0 steps failing:
  [`logs/dry-listing-e182.txt`](logs/dry-listing-e182.txt). The runbook's steps with k6's steps 5 and 9 and the guard: dmcmd_audit GO, 11 sites,
  every one READ, all in E128's guard.

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** the stock-take's INVENTORY.md, read Sat 7 Nov 2026 about 13:30 PST (E182.md's block). Public rows read: P11, P12, H06, H07,
   H08, H09, H15, H16, H18, H21, H24, H27, H28, L11. The row ids are opaque pointers into a private inventory. Pieces newer than it are cited
   by commit: E178's data (`f7820e70`) and kit (`a4aafc6f`, note 1 `763307e7`), E184's kit (`65f844be`, for kit v5's lessons table).
2. **Used** (each unchanged, called, sourced or imported by path; its sha256 in `harness-e182.json` or [`SHA256SUMS-e182-kit`](SHA256SUMS-e182-kit)):
   - **E178's kit** (`tools/claims-v3/e178/`, the form of every box and desk file here: the runner, block, queue, session, check, preflight,
     smoke gate, reducer, collector v2, harness maker, dry pass and the v2 runbook steps), and from it, unchanged: `scrub_tree_e178.py` (the
     login scrub over every directory) and `score_e178.session_scale` (M10's term a, predict_pool8's scale over E78's random float anchors).
     *Check:* E178 ran this form on aifoundry3 on 6 Nov 2026 (45.2 card-minutes, every command a read, C 3,130 of 3,130 PASS).
   - **E78's card code and reduction** and E163's reused files and four box binaries, through `make_harness_e182.py`, which refuses unless
     every value equals E178's harness.
   - **Q139(k)'s check of C** (`ccheck.py`, `sparsity_ccheck.sh`, `patch_host_ccheck.py` and its mock runtime, unchanged). *Check:* the
     mock runtime's own end-to-end test is Q139(k)'s; here the patched train host passes ccheck.py on every launch (above).
   - **`ccsessions_p8.py`** (Q142(k6)), imported unchanged, its listing widened in memory for the train blocks (`ccsessions_e182.py`).
   - **The k6 runbook's v3 drivers** (`q141k-runbook/k6/rb_common.sh`, its steps 5 and 9), sourced unchanged.
   - **Q136(w)'s `dmcmd_audit.py` and table, and E128's `ettelem_guard.sh`**: the audits.
   - **E182's registration** (`58b88850`): `kinds-e182.json` and the tiles, `plan-e182.json`, `forecast-e182.json`, `power-e182.json`,
     `noise/noise-e182.json` and `e182_stats.py`, each checked against the registration's hash list first (`e182_common.check_frozen`).
3. **Not used:** E172's card-1 kit (E182 is kitted for aifoundry3 only); E180's and E184's kits' code (E184's lessons table is followed, its
   enercat host change is not this host's); the PVT sampler (E182.md section 1, "Not used"); any train protocol of E102, E134 or E147.
4. **Tiers:** every file here is public tier and cites public pieces only. No NDA-tier check enters this kit.
5. **Readiness:** this block is the kit's. A verifier checks it against INVENTORY.md and the cited commits.

## Kit v5's lessons, item by item

| lesson | here |
|---|---|
| one copy of each C log | `collect_e182.sh` copies each listed session's C log once, gzipped, to `ccheck/c-log-<session>.jsonl.gz`, and copies the session directories without their `c-log.jsonl` (E178's data carried both, 15.5 MB) |
| s02 before s03 | step 3 (`rb/s03_desk_e182.sh`) refuses (10) unless step 2 wrote today's window in RB_OUT; the desk test's case K checks it |
| the commit message scanned | this commit's subject and body went through the public-text scan with the files; step 22 says so for the data commit's |
| a real floor-path dry case | the train host's real code path runs at the desk against the mock runtime (DESKTEST-HOST-E182), the reducer and scorer read full synthetic sessions in the box's layout, and the runbook's step 7 builds a box tree on which the box's own V3_DRY blocks run |
| one window file per runbook | E182's card day keeps its own RB_OUT (and so its own window file) and the one shared RB_LOCK |
| the readers' interpreter pinned | every desk command, the collector's default and every runbook step name `/usr/bin/python3` (3.9, with numpy for the scale); [`logs/interp-check-e182.txt`](logs/interp-check-e182.txt): the train reduction of a synthetic session under 3.9 and 3.13 differs only past the 13th digit (largest 9.6e-14 W; Python 3.12's compensated float sums), the units the same, which is why the pin binds |

## The scorer's readings, stated here before any datum (where E182.md leaves a choice)

- **The scored lines:** P, P + ACC and E at the session's s (M10's term a for fp32, from E78's random float anchors in the kinds passes,
  through `score_e178.session_scale` unchanged; 1 for int8; 1 when fewer than two kinds passes are kept) and each kind's measured rate in the
  kinds passes (the frozen rate when a kind has none); a train's line is its two kinds' scored lines' difference.
- **E182-C:** a launch's verdict is the check of C's for the same t_start_ms and t_end_ms; a kinds-pass launch belongs to its run's item, a
  train launch to the kind its record names (F or S), an anchor launch to its item. A train with any launch not PASS is NOT SCORED, and a
  kind not all PASS leaves every kinds-pass set.
- **A train process gives no value** when it has not exactly 13 launches after its calibration, when a record is not ok, or when its
  records' orientation differs from the plan's.
- **E182-W-int8's P line** is P's own slope over the int8 kinds scored (7.043 fJ at all 20); **E182-R-int8's line** is 0.4421 at 20 kinds,
  else the 97.5% point of 20,000 shuffles (random.Random(18205)); 4 or fewer kinds NOT SCORED.
- **E182-TR-N** pools each train's quads' residual sd (about its train's and its orientation's mean) by format; **E182-TR-H** pools the
  int8 trains' units (each less its train's mean) and takes the trains' median process period.
- **Reported, never a verdict:** E182-Q (the quartet fit per pass), E182-K (each pair's kinds-pass couples against its train), the
  couples' order term, the seven reduction arms' E182-W-int8 (E178's arms: session-own, dips removed, k frozen with dips, leak 0.1994,
  0.3803 and 0, gates off), every kind's D against P, P + ACC and E, and each train's reported readings (orientation means, halves,
  carry-over, process times, anchors, the rail's level).

## Card-minutes and the caps

| plan (`E182_PLAN`) | sequence | expected | cap (the budget rule) | the day's post says |
|---|---|---|---|---|
| **FULL** (default) | 18210-18215 (T4, T5, T3, T6, T2, T1), then 18220, 18221, 18222, then 18223 if it fits | **about 83-93** | **100** (6,000 s from E182_T0, 60 s reserve) | `for 2 h` |
| PASSES (the fallback) | 18220, 18221, 18222 | about 31 | 40 (2,400 s) | `for 1 h` |

The queue projects a train at its plan estimate plus 30 s (or the longest train measured, if longer) and a kinds pass at 640 s until one
ends, then the longest measured. A piece in flight is never cut; nothing is skipped ahead.

## The order on aifoundry3

E182 runs alone on aifoundry3, starting with `et-who` clean; an idle login does not block (D1, the owner's ruling of 1 Nov 2026). Never two
of our sessions on one card. The day's one post follows the one-post rule.

## The box steps that wait for the approvals and his go

Run them from the lab clone after `git pull --ff-only`, each with this card day's `RB_OUT` and `RB_LOCK`. The k6 drivers bound every remote
call: a 15 s hard-killed probe, then 60 s for a read, 600 s for a copy. A printed login link stops the step (11) and appends
`<HH:MM:SS> aifoundry3 needs a check` to `RB_LOCK`.

1. **His go and fresh network approvals** for aifoundry3. Then [`rb/s02_window_e182.sh`](rb/s02_window_e182.sh) `<day> <last start> <last end>`
   (FIRST: step 2 refuses without it).
2. **The desk check**, [`rb/s03_desk_e182.sh`](rb/s03_desk_e182.sh): the window written today; pull; HEAD descends from `58b88850`; E182's paths
   clean; the two hash lists; the harness rebuilt; the orders and trains verified; HARNESS OK 66; the host desk test's log. It reports
   note M1 present or absent and any E182 data in any ref.
3. **The day's one post** in `#community-lab` (the card lane's, under the post's lock):
   `using aifoundry3 for 2 h, until ~HH:MM PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`.
4. **Look first:** `../q141k-runbook/k6/s05_look_k6.sh aifoundry3 [--wait]` (k6's, unchanged).
5. **Sync:** [`rb/s07_a3_sync_e182.sh`](rb/s07_a3_sync_e182.sh), one rsync of every harness file but what the box builds.
6. **The train host's first compile and the checks on the box:** [`rb/s08_a3_preflight_e182.sh`](rb/s08_a3_preflight_e182.sh): `build_host_e182.sh`
   (BUILD OK), then `HARNESS OK: 73 files` (the four binaries, the train host's patched source and its build record), the preflight GO,
   the items verified. **If the build fails:** no train runs that day; run this step again with `--no-trains` (HARNESS OK 70) and step 9
   with `PASSES no`.
7. **Reads:** `../q141k-runbook/k6/s09_a3_reads_k6.sh` (k6's, unchanged).
8. **A V3_DRY pass on the box:** [`rb/s10_a3_dry_e182.sh`](rb/s10_a3_dry_e182.sh) `start`, then `wait` while it says 17: 18220's 70 launches,
   T1's train (4 and 64), the smoke (10 and 2), the start gate refusing (8).
9. **The session:** [`rb/s11_a3_session_e182.sh`](rb/s11_a3_session_e182.sh) `FULL yes` (or `PASSES no`). It launches
   `E182_T0=$(date +%s) E182_PLAN=FULL E182_TRAINS=yes E182_LATEST_START=<last start> E182_DEADLINE=<last end> setsid nohup bash tools/claims-v3/e182/session_e182.sh`
   detached. The session runs the check, the preflight, the stop-path test and the smoke with both gates before any block; a failed
   train gate turns FULL into PASSES.
10. **Wait:** [`rb/s20_wait_e182.sh`](rb/s20_wait_e182.sh), repeated while it says 17.
11. **Release, then collect:** the post's release. Then [`rb/s22_collect_e182.sh`](rb/s22_collect_e182.sh): the copies into `build/e182-raw`,
    `collect_e182.sh`, the C-session gate, the desk-path gate and the login scrub. The output is
    `build/e182-out/<day>-e182-one-number-r2-aifoundry3/`, and the data directory `docs/reports/data/<day>-e182-one-number-r2-aifoundry3/`. The
    public-text scan, the data commit's message with it, comes before its commit.

## Files, and what each builds on

| file | what | builds on |
|---|---|---|
| `e182_common.py` | the items (E78's, E178's six reused tiles, E182's 16), the registered kinds-pass order, the trains, the smoke, the frozen checks | `e178_common.py`; `plan_e182.py` |
| `run_e182.py` | the kinds runner (E78's unchanged, E171's live stops and watcher), and the stops the train runner shares | `run_e178.py` |
| `run_e182t.py` | the train runner: one process at a time through the wrapper with the train host, the stops before every process, the watcher | new |
| `patch_host_e182.py`, `build_host_e182.sh` | the host-only change and its box build | `patch_host_ccheck.py`, `build_host_ccheck.sh` |
| `block_e182.sh`, `queue_e182.sh`, `session_e182.sh` | one block (kinds pass, train, smoke, stop-path test), the plan's budget, the session | E178's three |
| `check_e182.py`, `preflight_e182.sh`, `smoke_gate_e182.py` | the harness check (and the train host), the device-command preflight, the smoke gate (kinds and train parts) | E178's three |
| `harness-e182.json`, `make_harness_e182.py`, `sync_paths_e182.py` | the sha256 of everything the box runs; the sync list | E178's |
| `reduce_e182.py` | E78's reduction on the kinds passes; the trains' reduction (`e182_stats.py`) | `reduce_e178.py` |
| `ccsessions_e182.py`, `collect_e182.sh`, `score_e182.py` | the C-session rule, the collection (one copy of each C log), every rule | E178's |
| `selftest_score_e182.py`, `fake_card_e182.py` | the scorer's self-test on E178's committed data and synthetic sessions | E178's self-test forms |
| `desktest_host_e182.sh`, `desktest_host_e182.py` | the train host against the mock runtime | Q139(k)'s mock runtime and run_e2e.sh |
| `dry_intel_e182.sh` | the Intel dry pass with stand-in ssh, rsync and scp | `dry_intel_e178.sh` |
| `rb/` | steps 2, 3, 7, 8, 10, 11, 20, 22, the dry listing, the desk test with a fake ssh and rsync | E178's v2 runbook (k6's drivers) |
| `logs/` | every check above | |
| `SHA256SUMS-e182-kit` | the kit's files, its logs and the unchanged files it calls | |

## Open items (for the verifier, the readiness critic and the records)

1. A verifier of this commit, then a readiness critic; card time only on his go, with fresh network approvals.
2. **The train host's first compile is on the box** (step 6). If it fails, the trains do not run that day and the session runs PASSES;
   every train rule reads NOT SCORED. A fix is a dated amendment.
3. **The collector has not run end to end on a raw tree** (its pieces have: the reducer and scorer on synthetic sessions, the C-session
   list, the smoke gate). Its first full run is the card day's step 22; a desk run on a synthetic raw tree is the verifier's to ask for.
4. The october-forecast-model (E182.md section 8): no note M1; if one comes, before the first datum, with its own reader.
5. Card 1 is not kitted.

## Compute

On the Intel through the round's local slot (`slot.sh`), one job at a time, at nice 10: the harness, the audits and the verify (seconds);
the train host's desk test (about 11 s: one compile against the mock runtime and seven short runs); the scorer's self-test (about 20 s);
the interpreter check (seconds); the Intel dry pass (about 2.5 minutes); the runbook's dry listing and desk test (about a minute). No bench
job, mini, lab box or card was used. The desk tests wrote only under the round's scratch.

SPDX-License-Identifier: Apache-2.0
