# Q141(k): the bounded runbook for the card day (E163-E169)

*Wed 4 Nov 2026 (week 45), PST, written and tested on the Intel, desk only: no card was claimed, no device command was sent, no
ssh reached a lab box, nothing was posted. Every command below comes from the kits as committed up to `c31e7ae3` (12:16:56 PST),
the dated notes over the READMEs. Nothing here changes a registration, a frozen file, a prediction, a stop or a rule of any run.*

It answers Q141(f)'s `desk_next` 1 (the readiness critic of 4 Nov) and its faults **F1** (box calls with no overall bound and no
probe), **F2** (E164's corrected collect line drops Q141(t)'s card-1 arm silently), **F4** (E166's box step 2 had no command),
**F5** (aifoundry2's wall time and the four dry passes before E165), **F7** (README step 5 still names the broken
`box/launch_e164.sh`) and **F9** (E165 already writes its zeros anchors; the step is writing them to a file). The critic's go
checklist is the order here; each of its box steps is one script.

## What it does to predicting power and heat

Nothing to any number: no frozen prediction, band, rule or verdict changes, and it makes no new blind test. It keeps the card
day unattended, so no call can hang on a Tailscale check (F1), and it closes two silent misses, Q141(t)'s card-1 arm in E164's
score (F2) and the E165 anchors arms of E167 and E168 (F9). The tests it carries are E163-E169's as registered.

## The rule every remote call follows (go checklist step 4)

Every step sources [`rb_common.sh`](rb_common.sh); every call goes through [`rb_run.py`](rb_run.py):

| | |
|---|---|
| **probe first** | `ssh -o BatchMode=yes -o ConnectTimeout=10 <box> true`, hard-killed at 15 s, before anything else reaches the box |
| **a bound on each call** | 60 s for a read, 600 s for a copy, 600 s for one wait (its loop on the box stops at 520 s), 60 s for a launch (it detaches on the box with `setsid nohup ... < /dev/null &` and returns at once), 5,400 s for a desk collector |
| **a login link** | a Tailscale check URL on stdout or stderr kills the call at once (every process under it), appends `<HH:MM:SS> <host> needs a check` to the lock file `$RB_LOCK`, keeps the link in `$RB_OUT/links.txt` for the approval, and the step exits 11 |
| **never a prompt** | BatchMode, stdin from the script file or `/dev/null`, no terminal, `GIT_TERMINAL_PROMPT=0` |
| **a log line per command** | `$RB_OUT/runbook.log`: class, host, bound, seconds, exit status (its own and the child's) and the command |
| **no names** | what a call prints is kept with every et-who holder's login and command masked; the holder rule is read on the box as counts |

Set two variables first: `RB_OUT`, this card day's own directory outside the repo, and `RB_LOCK`, the file a login check is
appended to (on the Intel the round's tailscale-needed file). `RB_DRY=1` lists a step's exact commands and runs nothing.

**Exit codes** of every step: 0 done; 10 refused (usage, order, a missing input, a refusal on the box); 11 a login link (approve,
then run the same step again; section 9's retry is every 3 minutes for up to 45, and a detached run keeps going meanwhile); 12 the
probe got no answer; 13 a call ran past its bound and was killed; 14 a call exited non-zero (its status is in the log); 15 a holder
for 30 minutes in all: skip that card; 16 a gate says stop (read the message); 17 not yet: call the same step again.

## The steps, in the go checklist's order

Run each from the top of the Intel's lab clone as `bash tools/claims-v3/q141k-runbook/<script> <args>`.

| # | who | script | what it runs (the kit's own commands) |
|---|---|---|---|
| 1 | him | `s01_probe.sh` | the three probes; every link printed goes to him (each approval lasts about 12 h) |
| 2 | him | `s02_window.sh <day> <last start> <last end> [full\|a\|b]` | records his go's window and plan; refuses a plan the window cannot hold |
| 3 | session | `s03_desk.sh` | `git pull --ff-only`; HEAD descends from `c31e7ae3`; `tools/claims-v3` clean; blind7 91, `frozen-sha256-e168.json` 9, the scorer list 18, predict_q140e's 26 |
| 4 | — | (the rule above) | every remote call below |
| 5 | session | `s05_look.sh <box> [--wait]` | et-who, who, uptime (aifoundry1: `box/look_e164.sh` too); the holder rule |
| 6 | session | **not scripted** | the day's one post, under the Discord lock, by the main session; every launch below waits for it |
| 7 | session | `s07_a3_sync.sh` | aifoundry3's ONE rsync: E163's step-4 paths and `tools/claims-v3/e166/` (F4) |
| 8 | session | `s08_a3_preflight.sh` | blind7 91; `check_e163.py` HARNESS OK 142; `preflight_e163.sh` GO; `e163_common.py --verify`; `frozen-e166.sha256` 30; `preflight_e166.sh` GO |
| 9 | session | `s09_a3_reads.sh` | `et-lab-manifest` (kept on the box); `ettelem config` through E128's guard, as the sessions read it (TDP 0 W, 65 C, 600 MHz); et-who |
| 10 | session | `s10_a3_dry.sh start\|wait` | the V3_DRY E166 session; V3_DRY `block_e163.sh` 16310, 16350, 16301 --smoke; the start gate's exit 8 |
| 11 | session | `s11_a3_session.sh e166 [--later-try]`, then `e163 [FULL\|TWO\|SHORT]` | the detached sessions (README box step 5 / step 10) |
| 12 | session | `s12_a1_check.sh sync\|start\|wait` | `box/sync_e164.sh`; `box/check_box_e164.sh` (the harness, preflight, tiles, blind7, the dry pass) |
| 13 | session | `s13_a1_launch.sh [--drop-p2]` | `ssh ... aifoundry1 "bash -s -- '<deadline>'" < box/launch_e164_a1.sh`, never `box/launch_e164.sh` (F7) |
| 14 | session | `s14_a2_tree.sh` | the tree and every aifoundry2 preflight (E165, E167, E168, E169), et-lab-manifest, et-who |
| 15 | session | `s15_a2_dry.sh <e165\|e167\|e168\|e169> start\|wait` | the four dry passes, two at a time, before E165's session (F5) |
| 16 | session | `s16_a2_e165.sh [full\|subset]` | E165's slot and detached queue (`--cap 40`, or the subset's `--cap 25`) |
| 17 | session | `s17_a2_e167.sh latch`, `config`, `go <4 HH:MM>` | `latch_check_e167.py`; `run_e167.sh config start`; `run_e167.sh go` and the GO marker |
| 18 | session | `s18_a2_e168.sh` | E168's 66-minute slot and detached queue |
| 19 | session | `s19_a2_e169.sh` | E169's 45-minute slot and detached queue (`build/e169/runs` must not exist) |
| 20 | session | `s20_wait.sh <run>` | one bounded wait, repeated; it prints each smoke gate's verdict |
| 21 | session | **not scripted** | the releases: rewrites of the day's post |
| 22 | session | `s22_collect.sh <run>`, then `pair` | collect and score at the desk (below) |

## The gates the scripts hold

- **The window** (`s02_window.sh`, from his go): no card session starts after the round's last start, and every slot and session
  must end by its last end (each launch refuses otherwise). E163_LATEST_START and E166_LATEST_START are the last start;
  E163_DEADLINE and E166_END_GATE the last end; E164's deadline is the last end less 10 minutes.
- **The holder rule** (`s05_look.sh`): a holder of a device node or a card lock blocks; on aifoundry1 a holder of card 1's nodes or
  lock, or anything of ours on either card, blocks (launch_e164_a1.sh's rule; card 0 is never used). An idle login does not block.
  `--wait` polls every 30 s on the box inside one bounded call; after 30 minutes in all the step says skip that card (15).
- **aifoundry3**: E166 first, on a rested card (G0 needs the room at or under 53.0 C). `s11_a3_session.sh e163` refuses until
  E166's session has ended, unless the plan is (a), E163 instead of E166. If `s20_wait.sh e166` reads G0's refusal (exit 7 in
  the log), E163 goes next; a later E166 needs at least 40 minutes of rest after E163's session end and the earlier smoke moved
  aside (`--later-try` checks the first and does the second: `p16601 -> p16601.try1`).
- **aifoundry1 card 1**: one session of ours (E164); the launcher's own refusals open nothing (exits 2, 3, 4, 9).
- **aifoundry2**: `s16_a2_e165.sh` refuses until every planned dry pass has ended rc 0 (full: all four; plan b: E165's and
  E167's; plan a: E165's). No dry pass starts while a card session of ours runs on that box, and no session starts while a dry
  pass runs there. E167 needs the latch check after E165's queue (GO or UNREADABLE; NO-GO skips E167 that day and goes on to
  E168), and its four gates are given, never defaulted, inside the window. E168 waits for E167's queue to end, E169 for E168's.
- **E164's collection** waits for E163's (its X1/X2, RK4 and `--other-drop` read E163's files); the `pair` step waits for both.

## The times, from his go (Q141(f)'s card plan)

| card | from his go (T, the approvals done) | card-minutes (caps) |
|---|---|---|
| all | T+0-10 desk checks, probes, the look-first reads, the day's one post with three clauses: `using aifoundry3 for 3 h`, `using aifoundry1 card 1 for 1.5 h`, `using aifoundry2 for 4 h`, each with its `until ~HH:MM PST` | |
| aifoundry3 card 0 | T+10-20 the sync, preflights, reads and both V3_DRY passes; **E166** T+20-95 (74.4 of 76, no subset); **E163** FULL T+97-156 (56-59, cap 70); release about T+158 | 131-134 (146) |
| aifoundry1 card 1 | T+10-15 the sync and the check; **E164** T+20-78 (57.6, cap 65; four 96-run passes); release about T+80 | about 58 (65) |
| aifoundry2 card 0 | T+10-17 the tree and preflights; T+17-27 the four dry passes, two at a time; **E165** T+28-65 (about 36; cap 40 in a 45-minute slot); the latch check; **E167** T+68-140 (35-39 of 40 card-minutes, about 66-75 minutes of wall time: E98's two 15-minute rests); **E168** T+142-190 (about 42, 53 at every cold gate's bound; cap 58, at most 63 in a 66-minute slot); **E169** T+193-208 (11-16, cap 20); release about T+210-230 | 123-148 (173) |

The last release comes about 3.5-4 h after his go; collection and scoring follow on the Intel, about 1-1.5 h at nice 10 with at
most 2 jobs. **His window:** the full plan needs the last end at least about 4 h 15 min after his go and the last start at least
3 h 30 min after it. **Subsets:** (a) about 1.5 h (a window of about 1 h 45 min): E163 (FULL, or TWO) on aifoundry3 instead of
E166, plus E164 and E165; (b) about 2.75 h (a window of about 3 h): everything but E168 and E169; (c) all seven.

## Collect and score (go checklist step 22)

After each run's `s20_wait.sh` reads 0. On the Intel, at nice 10, at most 2 jobs; every copy bounded; nothing committed here.

| run | `s22_collect.sh` runs |
|---|---|
| e163 | the dated note's two copies into `build/e163-raw`, then `collect_e163.sh <raw> docs/reports/data/2026-11-04-q141t-s7-recount/arm/arm27-aifoundry3.json`; it reads `results.md written` (collect_e163.sh exits 0 even when the scorer fails, F6) |
| e166 | `collect_e166.sh <data dir>`; it reads `score rc=0` (F6) |
| e164 | `box/pull_e164.sh`, then `PY=/usr/bin/python3 PYS=<3.12+> E164_DATE=<day> E164_S_RECOUNT=docs/reports/data/2026-11-04-q141t-s7-recount/arm/arm27-aifoundry1c1.json nice -n 10 bash collect_e164_a1.sh build/e164-raw <E163's e163.json> <its C-excluded tiles> <E163's scored.json>` (F2); the C-excluded tiles are E163's `scored.json` › `primary.c_excluded`, comma-joined |
| e165 | `collect_e165_bounded.sh <a new, empty scratch dir> <data dir>` (never `collect_e165.sh`), then [`anchors_e165.py`](anchors_e165.py) writes `score.anchors` to `anchors-for-e167-e168.json` and `score.anchor_delta` to `anchor-delta-e165.json` in E165's data dir (F9) |
| e167 | `collect_e167_bounded.sh <data dir> <from> <to>` (the span read from E167's `queue.jsonl`; the runs copy bounded at 600 s), `ccheck.py check` on each step's C log (`--jobs 2`), `sha256sum -c frozen-e167-x2.sha256`, then `score_e167_x2.py <data dir> --e165-anchors <that file> --json <data dir>/scored.json` |
| e168 | a bounded copy of `build/e168/runs` only, E111's login scrub, `launches.jsonl` and `tel/*.jsonl` gzipped as E159's sessions, then `reduce_e168.py <dir>/aifoundry2 --out results.json --anchors <that file> > reduce.txt` |
| e169 | a bounded copy of `build/e169/runs` only (never `build/e169/dry`), the same scrub and gzip (E158's committed layout), then `score_e169.py <dir>/aifoundry2/s[1-6] --out results.json > score.txt` |
| pair | after E163 and E164: `score_rank4.py --a3 --c1 --pair E163/E164` and Q141(t)'s `score_s7arm_a1.py --a3 --c1`, into `build/q141k-out/<day>/` |

Before any data commit, read `logs/` for et-who lines: E163's and E166's with E164's scrub in `--check` mode (F3; it needs our box
login, which `s05_look.sh` records in `$RB_OUT`), E164's by its own collector (exit 7 = commit nothing); then the public-text scan.

## Where the runbook adds to the kits' commands (none touches a device)

- **Dry passes run detached.** E163's and E166's V3_DRY passes, E164's `check_box_e164.sh`, and aifoundry2's four dry passes are
  the kits' commands, run on the box as one detached job each (`build/q141k/jobs/`) and waited on with bounded calls, so no call
  waits minutes in the foreground. An earlier dry directory of the same pass is moved aside first (its records would be read as
  this pass's). E165's dry pass is stopped after its smoke and stop tests with the queue's own `RUNS/QUEUE-STOP` (touched once the
  queue is in its slot; `full` runs the whole dry queue).
- **The launches** add `mkdir -p` before the output redirect (E169's dated note gives the reason), refuse a runs directory that
  already holds a queue, and record the session log's length so a wait reads only this session's lines.
- **E168's and E169's copies** use E165's bounded collector's remote rsync form (`--rsync-path="nice -n 19 rsync"`); E169's copy
  gets the scrub and gzip E168's README names (both queues' docstrings say a login in E64's end reason is scrubbed at collection).
- **E167's data directory** is named `<day>-e167-heat-replicate-aifoundry2` after E166's (its kit names none).
- **Rank 4's pair** runs with Python 3.12, as E164's pair scorer runs `score_rank4.py`; everything else with `/usr/bin/python3`
  (3.9.6, numpy), as the kits name it.

## Device commands sent

The runbook sends no command of its own. A device-touching step only calls the kits' audited scripts on the box: the sessions,
queues, launchers and dry passes, and in step 9 E128's guard with `config` (the call `session_e163.sh` and `session_e166.sh`
make). `dmcmd_audit.py` on the runbook's files with that guard scanned beside them, as E163's and E166's preflights scan it
([`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt)): **GO, 11 send sites, 0 disallowed, no allow-list, no exception**, every one a
line of `e128/ettelem_guard.sh` (its `config` at line 18 and `sample` at line 31, already in E163's audit) and every command READ.
Without the guard ([`logs/dmcmd-audit-bare.txt`](logs/dmcmd-audit-bare.txt)) it reads NO-GO at exactly step 9's call, the
guard's binary unresolved, as any caller of the guard reads when the guard is not scanned with it.

## The desk tests

- [`selftest_runbook.sh`](selftest_runbook.sh) → [`logs/selftest.txt`](logs/selftest.txt): **152 of 152 checks pass**. A stand-in
  `ssh` and `rsync` first on PATH take every call; the stand-in ssh runs a remote script in a stand-in box (stub et-who, who,
  uptime, sudo and setsid; GNU date) and feeds it through a pipe, as ssh's channel does. The cases: success (the probes, his
  window, FREE with idle logins, a held card polled until free, a held card skipped after 30 minutes in all, the one rsync, a
  detached job and its wait, `launch_e164_a1.sh` itself delivering the whole deadline `'<day> 16:20 PST'` to the session,
  E165's slot line by the queue's own pattern, a wait that reads the end, look_e164.sh's raw et-who line masked); a login link
  and then a hang (at a probe, on a call's stderr and stdout, on rsync, on all three probes: each killed within a second, the
  lock line appended, the link kept); a hang with no output (the probe hard-killed at 15.5 s; a read, a copy, a launch and a
  wait each killed at its bound); a non-zero exit (a call's 7, rsync's 23 and ssh's own 255, each in the log, and the kit
  launcher's own refusal on a card-1 holder); and the desk helpers with no ssh at all (predict_q140e's 26 on the lab clone, the
  anchors written unchanged and none from a NOT SCORED E165, a 90-minute window fitting no plan, E167's gates out of order or past
  the window refused before any call). After every case no stand-in process is left, and no stand-in login is in any file the
  runbook wrote.
- [`list_steps.sh`](list_steps.sh) → [`logs/dry-listing.txt`](logs/dry-listing.txt): every step's exact commands, local and
  remote, with a sample window, and not one ssh or rsync call (the desk test checks it, case E).

Both ran on the Intel on one or two cores at nice 10, a few minutes in all (section 28: no batch work); no lab box, no mini.

## Files

| file | what |
|---|---|
| `rb_common.sh`, `rb_run.py` | the rule: the probe, the bounds, the link, the log, the masking; the remote prelude (the holder rule's counts) |
| `s01_probe.sh` … `s22_collect.sh` | one script per box step of the go checklist (steps 4, 6 and 21 have none) |
| `frozen26.py` | predict_q140e's 26 frozen inputs, parsed and hashed, never imported |
| `anchors_e165.py` | E165's `score.anchors` and `score.anchor_delta` to files |
| `list_steps.sh`, `selftest_runbook.sh` | the dry listing and the desk test |
| `logs/` | `selftest.txt`, `dry-listing.txt`, `dmcmd-audit.txt`, `dmcmd-audit-bare.txt`, `public-text-scan.txt` |

SPDX-License-Identifier: Apache-2.0
