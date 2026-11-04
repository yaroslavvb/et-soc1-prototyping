# Q141(k) v2: the card day's runbook, corrected

*Wed 4 Nov 2026 (week 45), PST. Written and tested on the Intel, desk only: no card was claimed, no device command was sent, no ssh
reached a lab box, nothing was posted. New files only: v1, the runbook one directory up ([`../README.md`](../README.md), lab
`e962227a`, 14:08:36 PST), is unchanged, byte for byte. Nothing here changes a registration, a frozen file, a prediction, a stop or a
rule of any run.*

v2 answers the faults Q141(k)'s adversarial verifier found in v1 (about 14:15-14:40 PST; its verdict: **holds with fixes**, five
minor faults and four nits, none touching a device command, a stop or a frozen number). v1 answered Q141(f)'s `desk_next` 1 and its
faults F1, F2, F4, F5, F7 and F9; v2 keeps all of that.

## Why v1 was not edited

The card half of 4 Nov 2026 began running v1 at 14:18 PST, ten minutes after its commit, on all three boxes:
- aifoundry1 card 1's lane: steps 2, 5 and 12, then E164's launch by step 13 at 14:19:42, then step 20's waits;
- aifoundry3's: steps 2, 5 and 7-10 (step 9 at 14:18:55, step 10's dry job 14:19:05-14:19:46), then E166's launch by step 11 at
  14:20:56;
- aifoundry2's: step 14 at 14:19:45 and again at 14:22:23, the four dry passes of step 15 from 14:22:54 to 14:31:31, E165 by step 16
  at 14:31:44, step 17 at 15:12.

E170's box kit, being written that afternoon by its own lane, sources v1's `rb_common.sh`. A change to v1's files would have changed
those lanes' next calls mid-run, and the record of what ran. So v1 stays as it ran, and v2 is its successor for any step a lane
chooses to switch to and for any later card day.

Two of the faults did not bite on 4 Nov: s12's wait read rc 0 at 14:19:02, 40 s before s13 (fault 1), and all six dry jobs that
day read JOB-DONE rc=0 (fault 2). aifoundry2's boot read `2026-10-26 15:13:03` at both of step 14's reads, so its identity holds
by the rule v2 adds (fault 5). Step 9 ran at 14:18:55, before E166's session (nit 1). E167's collection (fault 4) had not run by
15:25 PST.

## What v2 changes

| # | the verifier's finding | where | v2 | desk case |
|---|---|---|---|---|
| 1 | `s13` sends `launch_e164_a1.sh` with no check that the runbook's own dry job (s12's box check: V3_DRY 16410, 16401, 16402) has ended; every other launch has that guard | [`s13_a1_launch.sh`](s13_a1_launch.sh), [`s12_a1_check.sh`](s12_a1_check.sh) | one read on aifoundry1 first (60 s): no dry job of the runbook running, no card session of ours (E164's, or E170's queue on card 0), s12's check job ended rc 0 today; and s12's wait must have read the check clean today (it records that in `RB_OUT/a1-check-clean.txt`). A refusal exits 10 and sends nothing more | X3 |
| 2 | a dry job with no process and no exit status prints JOB-LOST, then JOB-RUNNING, and the wait returns 17 ("call again") on every call | [`rb_common.sh`](rb_common.sh) `rb_job_wait` (s10, s12 and s15 waits) | the pid and the exit status are read again after a 2 s grace; a job confirmed lost prints JOB-LOST alone and the step exits 14; a job not started today exits 10 | X5 |
| 3 | a plain `s11 e166` with an earlier E166 smoke (`e166-smoke/p16601`) on the box reuses it: the old gate reads GO and the five stop tests do not run | [`s11_a3_session.sh`](s11_a3_session.sh) | a plain e166 is refused (10) when `p16601` is there (use `--later-try`), or when an earlier try's smoke was already moved aside (`p16601.try1`: a further try needs its own amendment). `--later-try` rests 40 minutes from the card's last session end of ours, E163's or E166's own, whichever is later (v1: E163's only) | X4 |
| 4 | `s22 e167` probes only aifoundry2, though `collect_e167_bounded.sh` also reads aifoundry1's and aifoundry3's history, and a login link from those boxes is written as "aifoundry2 needs a check" | [`s22_collect.sh`](s22_collect.sh), [`rb_run.py`](rb_run.py), `rb_common.sh` `rb_local` | all three boxes are probed first; `rb_run.py --host-from` takes the box for the lock line and the links line from the collector's own "TAILSCALE CHECK NEEDED (ssh <box> ...)" line (aifoundry2 when it names none), and the log line adds `link_host=` | X7 |
| 5 | nothing checks aifoundry2's firmware build (BL2 0.22.0): `et-lab-manifest` reads sysfs only, and `s14` printed `uptime -s` and compared it with nothing | [`s14_a2_tree.sh`](s14_a2_tree.sh) | identity by continuity, never the firmware-revisions query: the host must have booted before E69's firmware read (2026-10-27 13:56:26 PDT, which read release 1.4.0, BL1/BL2 0.22.0, PMIC 1.5.0, minions 0.25.1 inside the boot of 2026-10-26 15:13:03 PDT; E77's change record, "Firmware identities: by continuity"), as `look_e164.sh` holds aifoundry1 to E82's read. A later boot stops every aifoundry2 run (16): every aifoundry2 kit's commands are classified from BL2 0.22.0's source, and E168's README step 5 makes another build NO-GO | X8 |
| nit 1 | `s09` opens card 0 (the config read through E128's guard) with no check for a session of ours, as `s17`'s config read has | [`s09_a3_reads.sh`](s09_a3_reads.sh) | refused (10) while a card session of ours runs on aifoundry3 | X6 |
| nit 2 | "each launch refuses otherwise" did not hold for E163, which had no end check | `s11_a3_session.sh` | `e163` is refused (16) when its plan's budget from T0 would pass the round's last end: FULL 70, TWO 38, SHORT 30 card-minutes (E163.md, "Card budget and time gates"; FULL is registered for "a window of at least 70 card-minutes") | X10 |
| nit 3 | the wording "dmcmd_audit GO (no send site of its own)" | e962227a's commit message | below, § Corrections | — |
| nit 4 | the jobs' exit statuses, their scripts and E166's log offset carry no date, so a second card day would read the first day's | `rb_common.sh` (`fresh`, `job_ok_today`), `s11`, `s13`, `s16`, `s18`, `s19`, `s20` | the runbook's state on a box counts only if it was written today by the Pacific calendar (`TZ=America/Los_Angeles date -r`): another day's dry-pass verdict never admits a launch, and another day's offset, log end or queue status never reads as today's | X9 |

One change was not the verifier's: `ours_live` also counts E170's queue (`queue_e170.py`, `run_e170.py`), because the owner's go of
4 Nov 2026 put aifoundry1 card 0 back in use for E170, and never two of our sessions run on aifoundry1. The runbook has no E170 step;
E170 has its own kit. And every step's name carries `_v2` in the log and its messages (`step=s13_a1_launch_v2`), so a day's log
shows which runbook made each call.

## Using v2

The steps, their arguments, their order, the times, the collection commands and the device-command policy are v1's
([`../README.md`](../README.md): "The steps", "The times", "Collect and score"); call each under `v2/`:

    bash tools/claims-v3/q141k-runbook/v2/<script> <args>

with the same `RB_OUT` (this card day's directory, outside the repo) and `RB_LOCK` (the file a login check is appended to). The exit
codes are v1's, and two now say a little more: **10** also means "not started (or launched) today", and **14** also means "the dry job
is lost: read its `.out` on the box, then start it again".

**Switching during a day.** v2 reads the same state on the boxes as v1 (`build/q141k/` under each tree) and takes what was written
that day, so a lane that began on v1 can go on with v2 at any step. Two things to know: v2's `s13` needs s12's clean read recorded
by v2's `s12_a1_check.sh wait` (one bounded read, if s12 ran on v1), and v2's `s11 e166` refuses a plain later try that v1 would
have launched. For 4 Nov's card half the step this matters for is **E167's collection**: `v2/s22_collect.sh e167` probes all three
boxes and names the right box in the lock line, and otherwise runs v1's commands into the same data directory.

## What it does to predicting power and heat

Nothing to any number: no frozen prediction, band, rule, stop, registration or verdict changes, and no new blind test is made. It
makes the card day's gates hold as the go checklist states them: no launch beside the runbook's own dry pass (E164's included), no
reuse of an earlier E166 smoke (so E166's five stop tests run on every try), no aifoundry2 run whose firmware identity is not carried,
no E163 FULL in a window it cannot fill, and no state of another card day read as today's. The blind scores E163-E169 measure stay
E163-E169's own.

## Device commands sent

v2 sends no command of its own. A device-touching step only calls the kits' audited scripts on the box, and in step 9 E128's guard
with `config`, as `session_e163.sh` and `session_e166.sh` do. [`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt): `dmcmd_audit.py` on
v2's files with that guard scanned beside them: **GO, 11 send sites, 0 disallowed, no allow-list, no exception**, every one a line
of `e128/ettelem_guard.sh` (its `config` at line 18 and `sample` at line 31) and every command READ, as for v1. Without the guard
([`logs/dmcmd-audit-bare.txt`](logs/dmcmd-audit-bare.txt)) it reads **NO-GO at exactly step 9's call** (`v2/s09_a3_reads.sh:24`; 6
send sites), the guard's binary unresolved, as any caller of the guard reads when the guard is not scanned with it.

## Corrections to e962227a's own wording

- Its commit message says "dmcmd_audit GO (no send site of its own)". Read: **GO with E128's guard scanned beside the runbook, one
  device-touching call site, step 9's config read through the guard (`s09_a3_reads.sh:21`), a READ**; without the guard, NO-GO at that
  call. v1's README says this correctly.
- v1's README, "The gates the scripts hold", says every slot and session must end by the round's last end and "each launch refuses
  otherwise". That was not so for E163 (nit 2); in v2 it is.
- Q141(k)'s report counted five runs of its desk test; there were four.

## The desk tests

- [`selftest_runbook.sh`](selftest_runbook.sh) → [`logs/selftest.txt`](logs/selftest.txt): **324 of 324 checks pass**. v1's cases
  A-F run against v2 (success; a login link and then a hang; a hang with no output; a non-zero exit; the desk helpers and the window's gates;
  the dry listing), and X1-X10 for the verifier's cases and faults, with v1 run beside v2 where that shows the fault: X3v1 (v1's s13
  launched E164 beside a running check job), X4v1 (v1 launched E166 over the earlier smoke), X5v1 (v1 read a lost job as running),
  X6v1 (v1 read card 0 beside a session of ours), X7v1 (v1 wrote "aifoundry2 needs a check" for aifoundry3's link), X8v1 (v1 checked
  no identity), X9v1 (v1 read another day's "session end" as today's) and X10v1 (v1 launched E163 FULL with 60 minutes left). Case V
  checks that the twelve files v2 keeps from v1 are byte for byte v1's. The stand-in box runs on the Intel, so the test's `pgrep`
  counts only the test's own processes: other sessions on that Mac may run processes of the names `ours_live` looks for.
- [`list_steps.sh`](list_steps.sh) → [`logs/dry-listing.txt`](logs/dry-listing.txt): **50 of 50 steps exit 0**, and not one ssh or
  rsync call.
- [`logs/diff-v1-v2.txt`](logs/diff-v1-v2.txt): every change from v1, as a unified diff of each file v2 changes.
- [`logs/public-text-scan.txt`](logs/public-text-scan.txt): the public-text scan of v2's files and the dated note beside v1's README,
  **CLEAN** (8 matches, all the desk test's made-up stand-in login).

All ran on the Intel at nice 10 on one or two cores, a few minutes in all: no batch work, no lab box, no mini.

## Files

| file | what |
|---|---|
| `rb_common.sh`, `rb_run.py` | the rule, v1's with the changes above (`rb_job_wait`, `fresh`, `job_ok_today`, `ours_live`, `rb_refused`, `--host-from`) |
| `s09`, `s11`, `s12`, `s13`, `s14`, `s16`, `s18`, `s19`, `s20`, `s22` | the steps v2 changes |
| `s01`, `s02`, `s03`, `s05`, `s07`, `s08`, `s10`, `s15`, `s17`, `list_steps.sh`, `frozen26.py`, `anchors_e165.py` | v1's, byte for byte (case V). Their usage lines name v1's path; call them under `v2/` |
| `selftest_runbook.sh` | the desk test |
| `logs/` | `selftest.txt`, `dry-listing.txt`, `dmcmd-audit.txt`, `dmcmd-audit-bare.txt`, `public-text-scan.txt`, `diff-v1-v2.txt` |

SPDX-License-Identifier: Apache-2.0
