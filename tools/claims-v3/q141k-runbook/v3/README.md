# Q142(s) v3: the card day's runbook, made safe for the next card day

*Wed 4 Nov 2026 (week 45), about 19:20-20:45 PST. Written and tested on the Intel, desk only: no card was claimed, no device command
was sent, no ssh reached a lab box, nothing was posted. New files only. v1 ([`../README.md`](../README.md), lab `e962227a`) and v2
([`../v2/README.md`](../v2/README.md), lab `16771f36`) are unchanged, byte for byte. Nothing here changes a registration, a frozen
file, a prediction, a stop or a rule of any run.*

This answers the card half's critic (Q141's card half, 4 Nov 2026), next step 4: make the next card day's runbook safe. It also
answers the critic's incidents on the collection routes and on runbooks v1 and v2. The two complaints it fixes are on record:
- the e163 route, in E163's data README (§ Registered against what happened, D1:
  [`2026-11-04-e163-blind7-aifoundry3/README.md`](../../../../docs/reports/data/2026-11-04-e163-blind7-aifoundry3/README.md));
- the watcher race, in E165's D2, which has its own fix and amendment: [`../../hpl/run_hpl.py.dated-note.md`](../../hpl/run_hpl.py.dated-note.md).

## Results first

- **No verifier had read v2.** This read of it found 12 faults: 3 moderate, 6 minor and 3 nits. None of them touches a device
  command, a stop or a frozen number, and v3 fixes each one. Every fault has a desk case that passes on v3, and every fault but the
  structural one (2) has v2 run beside it to show it.
- **None bit on 4 Nov, as far as the committed records show.**
  - E163 was collected by hand over a repo-relative copy (its D1), so fault 1 never ran.
  - E166's and E167-E169's copies completed, and E167's committed history holds no raw file.
  - Both identity reads that day read ok.
- **The e163 route, the card-half critic's fault, is wider than the critic recorded.** The registered `reduce_e163.py`, run on one
  committed E163 pass by v2's absolute route, writes the clone's path into `e163.json`'s `dirs` (`reduce_e78.py:428`) and into all 97
  rows of `runs.csv` (its `dir` field, `reduce_e78.py:172`). By v3's repo-relative route it writes neither (case Y1r).
- **The desk test, [`logs/selftest.txt`](logs/selftest.txt): 453 of 453 checks pass.** A stand-in `ssh` and `rsync` sit first on
  PATH and no lab box is reached. The other checks:
  - the dry listing, 50 of 50 steps exit 0, with no ssh or rsync;
  - `dmcmd_audit` GO on v3's file set with E128's guard beside it (11 send sites, all the guard's, every command READ);
  - the public-text scan, CLEAN.

## What v3 changes

| # | severity | what v2 does | where | v3 | case |
|---|---|---|---|---|---|
| 1 | moderate | `s22 e163` copies into `$RB_REPO/build/e163-raw`, an absolute path, and hands it to `collect_e163.sh`. `reduce_e78.py` records the pass directories as given, so the Intel's home path would enter `e163.json`, every arm, `runs.csv` and the data directory (v1 line 55, v2 line 59: the card-half critic's) | `s22_collect.sh` | `build/e163-raw`, repo-relative, as E163's dated note names it. The step and every call in it run at the clone's top | Y1, Y1r |
| 2 | minor | Nothing checks that a desk path stays out of what a collector writes. Fault 1 is one case of this | `rb_common.sh` `rb_nopath`, [`nopath_q142s.py`](nopath_q142s.py) | After each collector, every file it wrote (`.gz` read through) is checked for the clone's path, `RB_OUT`'s, the user's home, any Mac home directory, the macOS temp tree and a session scratch root. A hit stops the step (16) before it says collected. A box's own `/home/<login>/` paths are left alone: the committed data holds them | Y1, Y2 |
| 3 | moderate | `collect_e166.sh` goes on after a failed rsync (it prints `rsync <x> rc=N`) and scores what arrived. v2 reads only `score rc=0`, so it reports a partial copy as collected and scored | `s22_collect.sh` e166 | A failed copy stops the step (14). The data directory holds a partial copy: remove it, then collect again | Y3 |
| 4 | minor | `s22 e168` and `e169` copy straight into the public data directory, then run E111's login scrub. A link or a bound killing the copy (11, 13) leaves an unscrubbed partial copy there, and nothing says so | `s22_collect.sh` e168/e169 | The copy, the scrub and the gzip run in `RB_OUT/<run>-raw/` (new, empty), which is removed whenever the step ends. Only a whole, scrubbed copy reaches the data directory. The copy of `queue.out` and the slot file is now checked too (v2 never read its exit) | Y4a, Y4b |
| 5 | minor | `collect_e167_bounded.sh` writes each box's raw 5 s history to `history/<box>.raw` in the data directory. The raw `held` field can name a holder, and the thinning reduces it to a bool. The file is deleted only after thinning or after a failed call. Its own exit 7, or `rb_run.py` killing it on a link or the bound, leaves the file there after E111's scrub has run | `s22_collect.sh` e167 | `history/*.raw` is removed whenever the step ends | Y5 |
| 6 | nit | That collector detects `login.tailscale.com` in any form, but its stop line prints only an `https://login.tailscale.com…` match. When that match is empty, `rb_run.py` sees no link, the step exits 14, and no lock line is written | `s22_collect.sh` e167 | A `TAILSCALE CHECK NEEDED (…)` stop appends `<HH:MM:SS> <box> needs a check` for the box it names (aifoundry2 when it names none) and exits 11 | Y6 |
| 7 | minor | `s05` on aifoundry1 stops only on a printed `identity: … STOP`. A `look_e164.sh` read that fails (14), or prints no identity line, passes, and the step reads the box FREE | `s05_look.sh` | The read must exit 0 and print `identity: … : ok`, else 16 | Y7 |
| 8 | minor | `ours_live` names only E163-E170's processes (`session_e16[346]`, `queue_e16[5-9]`, E170's two). A later card day's session (E171 on) reads as none, so the launch guards, the dry-pass guard and step 9's config read would all pass beside it | `rb_common.sh` | It also counts any `queue_eNNN.py` or `session_eNNN.sh` of ours, the lab's naming convention (dry ones excepted, as before) | Y8 |
| 9 | minor | The remote wait loops (`s05 --wait`, `rb_job_wait`, `s20`) add up their sleeps, not the clock. An et-who read may take up to 20 s, so `s05 --wait` can run past the call's 600 s bound and be killed (13) instead of reading 17 or 15 | `s05_look.sh`, `rb_common.sh`, `s20_wait.sh` | Each loop stops by the box's clock (`$SECONDS`) | Y9 |
| 10 | nit | `rb_run.py --stdout <file>` writes the command's stdout before it looks for a link, so a link on stdout lands in that file. `s22` writes `reduce.txt` and `score.txt` into a data directory this way | `rb_run.py` | A chunk holding a link is never written, and a call killed on a link or at its bound leaves no `--stdout` file | Y10 |
| 11 | nit | `s13` reads `launch_e164_a1.sh`'s refusals (its REFUSED lines) as 14, where the runbook's exit codes give 10 for a refusal on a box. Its end gate, 1,930 s before the last end, is 10 minutes looser than the launcher's own, which is 1,930 s before E164's deadline, the last end less 10 minutes | `s13_a1_launch.sh` | Refusals exit 10. The gate is 2,530 s before the last end | D4, Y11 |
| 12 | moderate | No launch re-checks the firmware identity. aifoundry1's is read only by `s05` without `--wait`, and aifoundry2's only by `s14`, with nothing making s14's 16 binding before `s15`/`s16`. A day that looks with `--wait`, or goes past a 16, launches on a host whose build is not carried | `rb_common.sh` `rb_guard_text`, `rb_launched` | Every launch on aifoundry1 and aifoundry2 checks the host's boot against its firmware read of record, on the box, in the call that holds its guard: E82's read of 2026-10-31 13:45:24 PDT, and E69's of 2026-10-27 13:56:26 PDT. A later boot, or no boot read, prints `IDENTITY-STOP`, launches nothing, and the step exits 16. aifoundry3 has no such rule in the go checklist and gets none here | Y12a, Y12b |

Also changed:
- `RB_BASE` can be set for a later card day's kit commit (default `c31e7ae3`, as v2).
- Every step's name carries `_v3` in the log and its messages.

## What the read checked and found sound

- **The bound on every remote call.** Each call goes through `rb_run.py` after a 15 s hard-killed probe, under its class's bound:
  probe 15 s, read 60 s, copy 600 s, wait 600 s, launch 60 s, desk 5,400 s. That covers:
  - the kits' local scripts that reach a box (`sync_e164.sh`, `pull_e164.sh`), bounded as a whole;
  - the collectors, bounded again inside (`collect_e165_bounded.sh`, `collect_e167_bounded.sh`, `collect_e166.sh`'s `timeout 300/120`).
  The only weakness was the loop accounting of fault 9.
- **Login-link handling.** Every step's ssh and rsync reach `rb_run.py` with stdout and stderr live, and a link kills the call,
  appends the lock line and exits 11. The two collectors that capture a call's stderr print the link in their stop line, so `rb_run.py`
  still sees it: `collect_e165_bounded.sh`'s probe, and `collect_e167_bounded.sh`'s `bounded()`. The one edge is fault 6.
  `--host-from` names the right box for E167's history reads.
- **The exit codes.** They are consistent across the steps, except fault 11. In v3:
  - 10 also covers a launcher's refusal;
  - 11 also covers a collector's check stop that printed no link;
  - 16 also covers an identity stop at a launch, and a desk path in a collection's output.
- **The go checklist** (Q141(f)): steps 3, 5 and 7-22 are scripted with its commands, its order and its gates. Steps 1, 2, 6 and 21
  belong to the owner or to the day's post, as in v1. Two places fell short of it, and v3 fixes both:
  - step 12's identity rule (fault 12);
  - step 22's "bounded copies only" read as also "complete copies only" (faults 3 and 4).
- **The kits' dated notes**, against the commands each step sends:
  - `launch_e164_a1.sh`, never `launch_e164.sh`;
  - E164's collect line with `E164_S_RECOUNT`;
  - `collect_e165_bounded.sh`, never `collect_e165.sh`;
  - E165's anchors written to files for E167 and E168;
  - E167's latch check on the UTC day's history file;
  - E169's empty `build/e169/runs`.

  They match, and so does E163's `build/e163-raw` once fault 1 is fixed.

## For the next card day

- **v3's steps name E163-E169's kits.** A later card day's runs (E171 on) come with their own kits. Port each step to them as v1
  ported the go checklist, and keep `rb_common.sh`, `rb_run.py`, `nopath_q142s.py` and the gates. Set `RB_BASE` to that day's kit
  commit.
- **A run on `run_hpl.py`** (the next governed bursts, heat holds, GEMM and stride runs on aifoundry2, and card 0's on aifoundry1)
  installs [`../../hpl/watcher_q142s.py`](../../hpl/watcher_q142s.py) as its dated amendment says, and its kit's frozen hash list
  carries the file. v3 launches E163-E169's frozen runners, so v3 itself does not change which watcher runs.
- **Not done here: aifoundry2's housekeeping** (the card-half critic's next step 9). The backup tar, `stash@{0}` and the old
  `reduce_e77.py` copy in `~/claude/work` stay on the box, because this round touched no lab box. It is one bounded box step for the
  next lane on aifoundry2: our own files only.

## Using v3

The steps, their arguments, their order, the times, the collection commands and the device-command policy are v1's
([`../README.md`](../README.md): "The steps", "The times", "Collect and score"). Call each under `v3/`:

    bash tools/claims-v3/q141k-runbook/v3/<script> <args>

Use the same `RB_OUT` (this card day's own directory, outside the repo) and `RB_LOCK` (the file a login check is appended to). v3
reads the same box state as v1 and v2 (`build/q141k/` under each tree), so a lane can switch at any step. The exit codes are v2's,
with the additions listed above.

## What it does to predicting power and heat

Nothing to any number: no frozen prediction, band, rule, stop, registration or verdict changes, and no new blind test is made. What
it keeps:
- the blind tests' data directories free of desk paths;
- a partial copy out of any score;
- no launch on a host whose firmware build, which classifies every device command, is not carried;
- a later day's sessions counted by the guards.

So the next card day's measurements of power and heat arrive as registered.

## Device commands sent

v3 sends no command of its own. A device-touching step only calls the kits' audited scripts on the box, and in step 9 E128's guard
with `config`, as v2 does. The identity lines added to every launch read `uptime -s` and `date` only.

[`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt) has `dmcmd_audit.py` on v3's files with that guard scanned beside them: **GO, 11 send
sites, 0 disallowed, no allow-list, no exception**. Every one is a line of `e128/ettelem_guard.sh` and every command is READ, as for
v1 and v2. Without the guard ([`logs/dmcmd-audit-bare.txt`](logs/dmcmd-audit-bare.txt)) it reads **NO-GO at exactly step 9's call**
(`v3/s09_a3_reads.sh:24`, 6 send sites), as v2's does.

## The desk tests

- [`selftest_runbook.sh`](selftest_runbook.sh) → [`logs/selftest.txt`](logs/selftest.txt): **453 of 453 checks pass**.
  - v1's cases A-F and v2's X1-X10 run against v3, with v1 beside it where v2's test did. D4 now expects 10.
  - Y1-Y12 cover the faults above, with v2 beside it.
  - V checks that the 18 files v3 keeps from v2 are byte for byte v2's.
  - It uses four stand-ins in its scratch repo, for collectors and scorers the cases do not need to run for real.
  - Y1r runs the registered `reduce_e163.py` on the committed pass p16310.
  - The stand-ins' sleeps (3637 and 3638 s) differ from v1's and v2's tests, so no test's clean-up touches another's.
- [`list_steps.sh`](list_steps.sh) → [`logs/dry-listing.txt`](logs/dry-listing.txt): **50 of 50 steps exit 0**, and not one ssh or
  rsync call.
- [`logs/diff-v2-v3.txt`](logs/diff-v2-v3.txt): every change from v2, as a unified diff of each file v3 changes.
- [`logs/public-text-scan.txt`](logs/public-text-scan.txt): the public-text scan of v3's files, the dated note beside v2's README and
  the watcher fix's files, **CLEAN**.

All ran on the Intel through the round's local slots: one job at a time, nice 10, one core, about 5 minutes for the desk test. No
batch work, no lab box, no mini.

## Files

| file | what |
|---|---|
| `rb_common.sh`, `rb_run.py` | the rule: v2's, with `ours_live`, `rb_job_wait`, `rb_guard_text`, `rb_launched`, `rb_identity_stop`, `rb_nopath`, `RB_BASE` and `--stdout` as above |
| `nopath_q142s.py` | new: the desk-path check over a collector's outputs |
| `s05`, `s13`, `s20`, `s22` | the steps v3 changes |
| `s01`-`s03`, `s07`-`s12`, `s14`-`s19`, `list_steps.sh`, `frozen26.py`, `anchors_e165.py` | v2's, byte for byte (case V). Their usage lines name v1's or v2's path; call them under `v3/` |
| `selftest_runbook.sh` | the desk test |
| `logs/` | `selftest.txt`, `dry-listing.txt`, `dmcmd-audit.txt`, `dmcmd-audit-bare.txt`, `diff-v2-v3.txt`, `public-text-scan.txt` |

SPDX-License-Identifier: Apache-2.0
