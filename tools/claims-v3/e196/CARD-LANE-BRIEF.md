# E196's card-lane brief: what the lane that runs E196 on aifoundry3 does, step by step, and what it never does (Q185; kitted, not run)

*Sun 15 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q185, lane `kit-e196`), beside [KIT.md](KIT.md). The registration is
[E196.md](E196.md) (its subtree `6f692709...`, list `SHA256SUMS-e196-registration` `467ede78...`, 49 entries). No card was claimed or
opened, no device command was sent, no other box was reached, nothing was posted. No E196 datum exists. This brief changes no arm, value,
order, window, threshold, host assignment, stop, cap, rest or the reduction. The forecast stays sealed: no forecast number is in this file.
Before the land, Q191's lane `fix-e196` (Sun 15 Nov 2026, before any E196 datum) moved this brief to the registration as fixed (redaction
R1, notes 1-4: the subtree and list above) and named the undesk on the failure paths of steps 1 and 2 (verify-e196's finding 7).*

## 1. What the go must carry (E196.md 12)

- **The owner's go** for E196 on **aifoundry3 card 0, at 600 MHz as found, reads only, nothing set**: on the round's reading, his standing
  words of Sun 15 Nov 2026 10:22:36 PST ("don't worry about discord post, just use the machines, nobody is using them") with E196's
  registered items as its defaults, once it is registered, kitted, verified and readiness-checked. **About 49 card-minutes (46-53), cap
  60** from the first card command; **the 40-minute rests** (E196's first card command at least 40 minutes after the end of our previous
  session on aifoundry3, E195's in the round's order; the next of ours there, E197's, at least 40 minutes after E196's end); **one session**;
  **the window**: from G (the card lane's booking of aifoundry3, as E191's second session took it), last start G + 1:30, last end G + 3:00,
  both inside the Pacific day of G; **the post**: none, by the same standing words.
- **The freeze line in HEAD before any datum** (E196.md section 0): `5c5acc1622e526aa20917a646a077763a630468ca2435ba3c05511408b148aba` on
  one line of E196.md at the landed registration commit (`grep -c`); the registration and the kit both landed (ancestors of GitHub main);
  no `docs/reports/data/*e196*` path in any ref (step 2 checks it).
- **The anchor lines** (E196's LAND.md files give them with the landed commits): the registration's subtree `6f692709...` and list (49 of
  49 OK); the kit's list `SHA256SUMS-e196-kit` and step 2 (`rb/s03_desk_e196.sh`, outside that list) at their stated sha256, every entry OK;
  `SHA256SUMS-e196-shared` (17) every entry OK.
- **The kit's readings the go confirms or refuses** (KIT.md section 4): the kit's stop K1 in the smoke (0.5 cycles); the same-day rule (a
  launch with "no device opened" may be launched once more the same day; a session that opened the card and stopped at a gate is not tried
  again that day); a host output the runner cannot read writes no record (that run has no value); the end-stop 60 s before the cap.
- **The order on aifoundry3** that day: E195, then E196, then E197, each at least 40 minutes after the last of ours; never two of ours
  there at once (book.sh key aifoundry3).

## 2. The steps, in order (paths under `tools/claims-v3/e196/`)

Run from the lab clone (`cd $LAB`), ONE RB_OUT (a new directory outside the repo, E196's own), the one `RB_LOCK` (the round's file of
login checks) and, for step 2, `RB_GITLOCK` (the lab-git lock). Each step one plain call from a script file. k6's
drivers bound every remote call: a 15 s hard-killed probe, then 60 s for a read, 600 s for a copy, one bounded wait, a detached launch that
returns at once. **A printed login link stops the step (11) and appends `<HH:MM:SS> aifoundry3 needs a check` to `RB_LOCK`:** nothing is
retried until it is cleared, and a session detached on the box keeps running. k6's exit codes: 0 done; 10 refused; 11 a login link; 12 no
answer; 13 past a bound; 14 a call failed; 15 a holder for 30 minutes; 16 a gate says stop; 17 call again.

| # | the step | what to do with its exit |
|---|---|---|
| B | `bash W/book.sh take aifoundry3 <lane>` | 0 BOOKED; G = this moment. 1: another lane holds it: make no ssh call to aifoundry3 at all; stop |
| 0 | `W/onelab.sh desk <lane>` (THE ONE-LAB RULE: steps 0, H and 2 never overlap another lane's collect span or a commit of ours); `uptime` (THE LOAD RULE: above 8, wait in bounded chunks until below 6); GitHub main read; E196's anchor lines | any line not as stated: `W/onelab.sh undesk <lane>`, no box step that day: E |
| H | `bash W/hold.sh add <lane>` (THE QUIET HOLD, until the data commit); `git -C $LAB status --porcelain --untracked-files=all` reads 0 lines | not 0: hold.sh remove, onelab undesk, book.sh release, stop |
| 1 | `rb/s02_window_e196.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>` (today's day only; G + 1:30 and G + 3:00) | "fits now: E196 (its 60 card-minutes)"; "fits now: nothing": no box step: `W/onelab.sh undesk <lane>`, then E |
| 2 | `uptime`; then `rb/s03_desk_e196.sh` with `RB_GITLOCK`; **never inside the lab-git lock**; then `W/onelab.sh undesk <lane>` | anything but 0: no box step that day: `W/onelab.sh undesk <lane>`, then E; one exception: a pull whose output shows the upstream did not answer (step 2 again once it answers) |
| 4 | the look, `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` (it writes the box-login file step 11 reads) | FREE; a holder: bounded polls (`--wait`), at most 30 minutes, else no session that day |
| 3 | the day's post: **none**, by the owner's standing waiver of Sun 15 Nov 2026 10:22:36 PST; record his words | |
| 5 | `rb/s07_a3_sync_e196.sh` | 10: a session or runbook job of ours on the box; 16: uncommitted synced paths or a file off its sha256 |
| 6 | `rb/s08_a3_build_e196.sh start`, then `wait` while it says 17 | 0: RB_OUT/e196-built.txt (E196-BUILT: both hosts, both kernels' .text 8798e43c..., 42 of 42 refusals; BOXCHECK-E196 OK); 16: rebuild once (two starts a Pacific day at most; a third: NO-THIRD-BUILD, no session that day); a 14 on wait: no reading, wait again |
| 7 | **STEP 7 ONLY ONCE THE REST HAS OPENED** (40 minutes after the end of our previous session on aifoundry3, E195's): first `rb/s09_rest_e196.sh` (the rest rule read on the box, the lines step 9 sends; no card command), then at once `../q141k-runbook/k6/s09_a3_reads_k6.sh`, then 8 and 9 without delay. Step 7's configuration read is a card command (E192 data note 1's lesson); steps 0-6 and the rest read send none | s09_rest: 0 = opened (its "rest:" line, also in the runbook log); 10 = not yet: wait in bounded chunks and run it again, never step 7 before its 0. Then k6's (TDP 0 W / 65 C / 600 MHz; et-who clean): 16 = not as found: no session that day, set nothing; 17 = et-who not clean: step 4 with --wait, then s09_rest and step 7 again |
| 8 | `rb/s10_a3_dry_e196.sh start`, then `wait` | 0 (session_e196.sh --dry on the box: E196-DRY OK, 255 device calls, 237 cut, line for line the registered commands) |
| 9 | `rb/s11_a3_session_e196.sh` | 0 launched (its "rest:" line in the runbook log; the T0 in RB_OUT/e196-T0.txt); 10 refused (the rest, a session or job of ours, no dry pass or build today, the same-day rule): read why, never around it; 16: past the last start, or the cap would pass the last end |
| 10 | `rb/s20_wait_e196.sh`, again while it says 17 | 0: ended, MANIFEST-WRITTEN ("session stopped: ...; the blocks done stand" after a registered stop); 16 GATE-STOPPED (no train and no pass block: no data; still collected, as a gate stop's record) or 16 MAIN-CRASHED (no registered stop: report it, kill nothing, collect it, a dated note decides); 14: gone without "session end" (read the box read-only) |
| 11 | `W/onelab.sh collect <lane>`; then `rb/s22_collect_e196.sh` (it must start 10 minutes before the last end) | 0 COLLECTED into `docs/reports/data/<day>-e196-zeroshare-aifoundry3/`, or for a gate stop into `docs/reports/gate-stops/<day>-e196-zeroshare-T<T0>-aifoundry3/`; 16: COPY-BACK NOT EXACT, the scrub, the desk-path gate, the history check, or a session log that does not say clearly how it ended: commit nothing, read why |
| 12 | the commit: README.md in [DATA-README-FORM-e196.md](DATA-README-FORM-e196.md)'s form (or its gate-stop form); the public-text scan; `LAB_QUIET_HOLD_OWNER=<lane> bash W/commit_lab.sh "<subject>" "<body>" <the collected directory>` (new files only; on exit 5 or 6 run it again); then `W/onelab.sh uncollect <lane>` | "COMMIT_LAB: pushed <sha>" |
| 13 | after the data commit only, never on a gate stop's record: `rb/s24_reduce_e196.sh docs/reports/data/<day>-e196-zeroshare-aifoundry3` | the registered reduction (`reduce_e196.py OUT --readback-none-ok`, unchanged) and the checker: RB_OUT/x14-e196.json, checks-e196.json and their printed lines; the records lane commits them beside the data; after a crash, only once a dated note says so |
| E | `bash W/hold.sh remove <lane>` after the data commit; `bash W/book.sh release aifoundry3 <lane>`; on every stop path, run both (and `W/onelab.sh undesk`/`uncollect` if held) after the last step that ran | |

**To stop the session by hand** (the operator's stop, a registered stop): `touch build/e196/T<T0>/run/STOP` on the box (the hosts read it
before every launch, the runner before every device process; the launch in flight finishes). Never kill a process: the session ends its own
device process and stops its sampler with SIGTERM.

## 3. After a gate stop, a registered stop, or a crash

- **A gate stop** ("GATE-STOP:" or "(no device opened)" in the wrapper's log; session.rc 2 or 3; no train and no pass block) is **no session:
  no data** (E196.md 11). Step 11 still collects it, into its **gate stop's record** under `docs/reports/gate-stops/`, never under
  `docs/reports/data/` (step 2 reads every `docs/reports/data/*e196*` path as an E196 datum). Commit the record (new files only, its README
  in the gate-stop form); it is never reduced. **E196 may be tried again with no amendment** (no train or pass block ran): after a launch
  that opened no device ("no device opened": the free check, the node count, the cut order's M < 40, a refusal), **once more the same day**,
  after the look reads FREE again and inside the window (step 9 counts them: a third is refused); after a gate that came after the card
  opened (the opening configuration read, the sampler, the smoke's heater or its gate or K1, the smoke's lock), **not the same day** (step 9
  refuses: the kit's same-day rule). A try on a later day needs the owner's go for that day and the rest.
- **A registered stop, the deadline, the end-stop or the cap** ("session stopped: ...; the blocks done stand"; session.rc 1, or 0 when the
  stop came between blocks): the blocks done stand and are reduced as they stand (E196.md 11); the data directory is committed; the missing
  blocks are never re-run without a dated amendment.
- **A crash** ("session ended without a registered stop": the port exited with no stop recorded; session.rc 4; step 10 says MAIN-CRASHED and
  16) is **not a registered stop**, and E196.md 11 has no row for it: **report it, kill nothing** (the port's own trap stops its sampler and
  makes or skips the closing read), collect it into its data directory and commit those records, then stop the day. **A dated note decides
  whether its blocks are reduced**; step 13 waits for it.
- **A launch that did not finish** (a host's "kernel did not finish", or `timeout` ending a device process: rc 124) may leave a hung hart:
  the session stops; **never reset the card, no PMIC or power action** (the field manual's gates). Keep the booking and the hold, write it up,
  escalate to the owner and the lab admin.

## 4. Never

- No step 2 but `rb/s03_desk_e196.sh`, and never inside the lab-git lock; no box step without step 2's 0 that day; no step out of the order
  above; never step 7 before the rest has opened (`rb/s09_rest_e196.sh` reads 0 right before it); never steps 5, 6 or 8 while a session of
  ours runs (they refuse).
- **No change to an arm, a value, the order, a window, a threshold, a host assignment, a stop, the cap or the reduction** except by a dated
  amendment before the data (E196.md 17); no block re-run after a stop or the deadline without one; the reduction only at its registered
  sha256 (`reduce_e196.py` `c58c6690...`) and only as E196.md 7 writes it (`--readback-none-ok`).
- No device command but the kit's READs (dmcmd_audit GO): no set, no reset, no governor, TDP, threshold, clock, voltage, fan or firmware
  change; no statistics reset (`--reset-ms`); no firmware query; no PMIC command; no power cycle and nothing that risks one; never kill a
  device process (no SIGKILL, no `timeout -k`).
- Never two sessions of ours on aifoundry3 at once; never beside another user's process or holder (the session's holder check and the
  port's before every block refuse); never on two cards (the session counts the nodes: exactly `/dev/et0_ops` and `/dev/et0_mgmt`).
- Never a lab user's login in any file (the collection's scrub masks every holder line's user and our own login, and refuses any /home/
  path left); never a forecast number of E196's sealed forecast in any lab file, and no scoring against it (the model session scores it
  privately after the data commit).
- Never touch another run's files on the box: E196 writes only E196's root (`build/claims-v3/aifoundry3/e196`), `build/e196/` and the
  runbook's own `build/q141k/` entries; never `build/sparsity`, which other kits use.
- Never run the reduction before the data commit, nor on a data directory that is not committed and clean; never on a gate stop's record.
- Never a card reset (a launch that did not finish is the owner's and the lab admin's to handle: stop, keep the records, report).

## 5. Labels

Every figure here is **registered** (E196.md) or a **desk check of code** (KIT.md). Nothing here is measured, blind, held out or post hoc.

SPDX-License-Identifier: Apache-2.0
