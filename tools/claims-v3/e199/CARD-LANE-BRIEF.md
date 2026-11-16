# E199's card-lane brief: what the lane that runs E199 on aifoundry1 card 1 does, in order, and what it never does (Q191; kitted, not run)

*Sun 15 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q191, lane `kit-e199`), beside [KIT.md](KIT.md). The registration is
[E199.md](E199.md) (its two freeze lines in section 0: the forecast, and the model session's sealed card-1 forecast, registered before
the land by fix-e199 on Mon 16 Nov 2026, with this brief's card time and step 1's stop path). No card was claimed or opened, no device command was sent, nothing was posted. No E199
datum exists. This brief changes no arm, value, order rule, window form, threshold, stop, rule, reduction, card time or cap.*

## 1. What the go must carry (E199.md section 10)

- **The go**: the owner's standing words of Sun 15 Nov 2026 ("continue, all machines are up", 10:05:42; "don't worry about discord post,
  just use the machines, nobody is using them", 10:22:36; "Feel free to use more cards in parallel, I don't need to reserve them",
  17:21:16) and his "Try again" (the round's CONTEXT section 122), with the registered items as defaults: **aifoundry1 card 1, 600 MHz as
  found, reads only, ET_DEVICES=1, card 1's lock; about 60 card-minutes (plan the booking and the rests on 60-65; E192 measured 59.52), cap 65** from the first card command (the start
  config read);
  **the 40-minute rests** on aifoundry1, either card; **no post** (waived, 10:22:36). E199 runs only after its kit, its verifier, its land
  and a readiness check.
- **The sampler's table for command 74**: E144's, the default (the per-sensor probe, then pvt when it answers); or the stock table alone,
  with `--plain-sampler` (command 74 never sent). KIT.md section 3.
- **A launch refused with "no device opened"** (exit 2, or 3 at the free check or at the config read's lock) sent no card command: the go
  may allow one more launch inside the same window once the look reads FREE again (E192's G4 form). A session ended by the identity gate (a)
  sent a command: no second session that day without a dated amendment.
- **The sealed card-1 forecasts** (the round's CONTEXT section 122): E199's, posted by the model session at 01:28:51 PST Mon 16 Nov 2026
  (#2.5.1.2.3, sha256 `1c5d8fa3...`), was registered before the land as E199.md's freeze line 2 (Q191, lane fix-e199): step 2 checks it
  and prints it; **no wait for it.** The orchestrator writes any later one to `W/out/orch/sealed-card1.txt`; one posted after E199's land
  enters only by a dated note at `tools/claims-v3/sealed-card1/e199-freeze-lines.md` (outside the pinned subtree), committed under the
  desk-commit rule BEFORE E199's card day; step 2 prints its sha256 as the later note's line.
- **The anchor lines** of E199's land files (the registration's and the kit's commits ancestors of HEAD; the subtree and list pins; step 2's
  sha256, outside the kit's list).
- **The order on aifoundry1 card 1**: the E191 repeat, then E198, then E199 (the round's plan), each 40 minutes after the last session of
  ours on aifoundry1 (wait for the rest, THEN book); one session of ours on aifoundry1 at a time, on either card.
- **The window from G = the booking on its day**: last start ceil(G+1:30), last end ceil(G+3:30), inside the Pacific day; the last start at
  most the last end less 70 minutes; no session that day when no start fits.

## 2. The steps, in order (paths under `tools/claims-v3/e199/`)

Run from the lab clone (LAB), each with this day's `RB_OUT` (a new directory outside the repo, E199's own), the one `RB_LOCK` and, for step
2, `RB_GITLOCK`. k6's drivers bound every remote call. **A printed login link stops the step (11) and appends `<HH:MM:SS> aifoundry1 needs
a check` to `RB_LOCK`:** nothing is retried until the check is cleared; a session detached on the box keeps running.

| # | the step | what to do with its exit |
|---|---|---|
| B | `bash W/book.sh take aifoundry1 <lane>` (G = its time) | 1 = another lane holds the box: stop |
| desk | **THE ONE-LAB RULE: `bash W/onelab.sh desk <lane>`**, right before step 0 | |
| 0 | THE LOAD RULE (`uptime`: the 1-minute load below 8, else wait in bounded chunks until below 6); E199's anchor lines exactly as LAND.md states; no E199 datum in any ref | any line not as stated: `onelab.sh undesk`, then E, stop |
| H | `bash W/hold.sh add <lane>`; LAB's status reads 0 lines | else `onelab.sh undesk`, remove the hold, release the booking, stop |
| 1 | `rb/s02_window_e199.sh <YYYY-MM-DD> <last start> <last end>` | first; today's day only; anything but 0: `onelab.sh undesk`, E, stop |
| 2 | `rb/s03_desk_e199.sh` with `RB_GITLOCK` set, under slot.sh, THE LOAD RULE first; **never inside the lab-git lock** (it takes it itself; nested it reads 16) | anything but 0: `onelab.sh undesk`, E, stop; one exception: a pull whose output shows the upstream did not answer (run once more when `git ls-remote origin` answers). Read its "sealed card-1 freeze lines" line into the result |
| undesk | **THE ONE-LAB RULE: `bash W/onelab.sh undesk <lane>`**, right after step 2 (and on every stop path from `desk` to here) | |
| 4 | `rb/s05_look_e199.sh` | FREE on both cards; HELD: `--wait` polls, at most 30 minutes in all, else no E199 that day; 16: aifoundry1 booted after E82's firmware read (THE REBOOT GATE): no launch, report |
| 3 | the post: WAIVED (the owner's words of 10:22:36), recorded in the result and the data README | never a post |
| 5 | `rb/s07_a1_sync_e199.sh` | 10: a session or job of ours on the box; 16: uncommitted synced paths or a file off its sha256 |
| 6 | `rb/s08_a1_build_e199.sh start`, then `wait` while it says 17 (after a 14, "no reading": wait again) | 0: RB_OUT/e199-built.txt (the hashes; BOXCHECK-E199 OK: ET_DEVICES in the host, the reader and the heater); 16: the build or the box check failed: read why; one more start a day only when the first did not build; a third: NO-THIRD-BUILD, no session that day |
| 7 | `rb/s09_a1_reads_e199.sh` | 0: card 1's config (IDENT-A OK: /dev/et1_mgmt, ID 1, TDP 65 W / 65 C / 600 MHz, minion_mv in (450, 510)); 10 "REFUSED: <m> minutes since ...": the rest has not opened (the config read is a card command): wait, then run it again; 16 "did not read OK" with no config: our own live collector may have held the node for a moment: run step 4 again and, when FREE, this step ONCE more; a second, or a read naming another card: no session that day |
| 8 | `rb/s10_a1_dry_e199.sh start`, then `wait` | 0 with `E199-DRY OK: 328 device calls` |
| 9- | step 10's reading (`ours_live 'session_e199.sh'`) against step 9's launch line (`setsid nohup bash .../session_e199.sh`): the same name | a mismatch: stop and report |
| 9 | `rb/s11_a1_session_e199.sh FULL` (`--plain-sampler` only if the go names it) | 0 launched (its rest line in the runbook log); 10 refused (the rest, a session or job of ours, no dry pass or build today): read why, never around it; 16 IDENTITY-STOP (the reboot gate): no launch |
| 10 | `rb/s20_wait_e199.sh`, again while it says 17 | 0: ended with its manifest (a STOP after passes: the passes done are reduced as they stand); 16: stopped before any pass (a refusal, the card not free, THE IDENTITY GATE (a) or (b), the watch, the smoke gate, a live stop before pass 0): still collect |
| collect | **THE ONE-LAB RULE: `bash W/onelab.sh collect <lane>`**, right before step 11 | |
| 11 | `rb/s22_collect_e199.sh` | 0 COLLECTED; 16: COPY NOT EXACT, the desk-path gate, the holder-line check, the scrub: commit nothing, read why (`onelab.sh uncollect`, E) |
| 12 | the data README from `rb/data-readme-form-e199.md`; the public-text scan; `LAB_QUIET_HOLD_OWNER=<lane> bash W/commit_lab.sh "<subject>" "<body>" docs/reports/data/<day>-e199-intbits-aifoundry1-c1` (new files only; on exit 5 or 6 run it again) | the data commit's sha in the result |
| uncollect | **THE ONE-LAB RULE: `bash W/onelab.sh uncollect <lane>`**, right after the data commit's push (and on every stop path from `collect` to here) | |
| 13 | after the data commit only: `rb/s24_score_e199.sh docs/reports/data/<day>-e199-intbits-aifoundry1-c1` (in the slot, a private /dev) | READ the transport verdicts (E199-T1, E199-T2, the families) as printed and in RB_OUT/scores-e199.json; a FAIL is reported as FAIL; a family NOT DECIDED as such; a records lane commits them with intbits-e199.json, checks-e199.json and the unfiltered reduction |
| E | `bash W/hold.sh remove <lane>`; `bash W/book.sh release aifoundry1 <lane>` | on every stop path too, after the last step that ran (a BOUND: keep the booking until the orchestrator says) |

## 3. Never

- No step 2 but `rb/s03_desk_e199.sh`, and never inside the lab-git lock; no box step without step 2's 0 that day; no step out of order;
  never step 5, 6 or 8 while a session of ours runs on aifoundry1 (they refuse); never a session of ours on aifoundry1 beside another.
- No device command but the kit's READs (`preflight_e199.sh`: the plain chain GO); **nothing to card 0** (no command, node or lock of it);
  **no set, reset, governor, TDP, threshold or clock move; no statistics reset; no firmware change; no power cycle and nothing that risks
  one;** never kill a device process (the kit stops through `OUT/STOP`; the launch in flight finishes).
- No arm, value, order, window, pass, smoke, threshold, stop or reduction but the registered: E192's reference session runs as committed.
- **No number of any sealed forecast and no score in any lab file but step 13's records**; the data README holds neither.
- Never another user's process or file; never a lab user's login in any committed file (our own box login is masked by step 11).
- Never touch another run's files on the box: E199's files live in its own root (`build/claims-v3/aifoundry1-c1/e199/`) and its sessions in
  `build/e199/`.
- Never run step 13 before the data commit, nor on a data directory that is not committed and clean.
- No simulator on any lab box; no host compute beside the run.

## 4. Labels

Every figure here is **registered** (E199.md) or a **desk check of code** (KIT.md). Nothing here is measured, blind, held out or post hoc.

SPDX-License-Identifier: Apache-2.0
