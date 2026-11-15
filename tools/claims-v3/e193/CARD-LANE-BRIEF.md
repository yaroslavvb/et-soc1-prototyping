# E193's card-lane brief: what the lane that runs E193 on aifoundry3 does, sitting by sitting, and what it never does (Q177; kitted, not run)

*Sat 14 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q177, lane `kit-e193`), beside [KIT.md](KIT.md). The registration is
[E193.md](E193.md) (its subtree `03ae7f5a...`, list `SHA256SUMS-e193-registration` `6258cde3...`, 29 entries). No card was claimed or
opened, no device command was sent, no other box was reached, nothing was posted. No E193 datum exists. This brief changes no arm,
value, order, window, threshold, stop, cap, rest or the reduction. Both forecasts stay sealed: no forecast number is in this file.
Fixed in place before the land (Q177, lane `fix-e193`, the same day): where a gate-stopped sitting's record goes and when a sitting is
tried again (section 3: verify-e193's finding 2), and a crash of the main run read apart from a registered stop (finding 5).*

## 1. What the go must carry (E193.md 12)

- **The owner's go** naming E193 on **aifoundry3 card 0, at 600 MHz as found, reads only**; **the two sittings, A then B** (A: blocks S,
  D, W, T, about 42 card-minutes, **cap 60**; B: block C, about 24, **cap 50**; about 70 card-minutes in all, at most 110); **the 40-minute
  rests** (before sitting A after any earlier session of ours there, between A's end and B's first card command, and after B); **one day
  or two**; and **the day's post route**: the post in the lab's channel, or his waiver of it for that day (his waiver of Fri 13 Nov 2026
  covered that day only; no post can be made from aifoundry2).
- **Both freeze lines in HEAD before any datum** (E193.md section 0): `d6ac4fb9f36d6a476610049cde780335faf218faed8482b45f4b03e405bf4362`
  (top-down) and `f7dc8210331cb512ebfe8f446189842df0e4eba118622a1da872f74d397bd73e` (from a gate-level simulation), each on one line of
  E193.md at the landed registration commit (`grep -c`); the registration and the kit both landed (ancestors of GitHub main); no
  `docs/reports/data/*e193*` path in any ref before sitting A, and none but sitting A's own before sitting B (step 2 checks both).
- **The anchor lines** the go names (E193's LAND.md files give them with the landed commits): the registration's subtree `03ae7f5a...`
  and list (29 of 29 OK); the kit's list `SHA256SUMS-e193-kit` and step 2 (`rb/s03_desk_e193.sh`, outside that list) at their stated
  sha256, every entry OK.
- **The order on aifoundry3** that day: after the sessions of ours already planned there (E189, E192), each with its 40-minute rest; never
  two of ours there at once. On one day with both sittings, sitting B's window (step 1 in its own RB_OUT) gives its last start at least
  sitting A's end + 40 minutes later; step 9 reads the rest on the box and refuses before it.
- **Sitting A's margin** (the lab's registered cap, KIT.md section 4): the runner's deadline (the first card command + 58 minutes) leaves
  about 10 minutes beyond the runner's own estimate (46 minutes of wall time, plus about 2 for the smoke) for idle-down waits; long
  idle-downs can cut the last pass, which is then reduced as it stands (E193.md 6). Sitting B's leaves about 18 (deadline at 48 minutes;
  the estimate 28, plus about 2 for the smoke).

## 2. The steps, in order, for EACH sitting (paths under `tools/claims-v3/e193/`)

Run from the lab clone, ONE RB_OUT PER SITTING (a new directory outside the repo, E193's own), the one `RB_LOCK` and, for step 2,
`RB_GITLOCK` (the lab-git lock). k6's drivers bound every remote call: a 15 s hard-killed probe, then 60 s for a read, 600 s for a copy,
one bounded wait, a detached launch that returns at once. **A printed login link stops the step (11) and appends `<HH:MM:SS> aifoundry3
needs a check` to `RB_LOCK`:** nothing is retried until it is cleared, and a session detached on the box keeps running.

| # | the step | sitting A | sitting B | what to do with its exit |
|---|---|---|---|---|
| 0 | by hand: `uptime` on aifoundry2 (THE LOAD RULE: above 8, wait until below 6), GitHub main read, the anchor lines | yes | yes | any line not as stated: no box step that day |
| 1 | `rb/s02_window_e193.sh <A\|B> <day> <last start> <last end>` | `A ...` | `B ...` (B's own RB_OUT) | first; today's day only; the window must hold the sitting's cap (A 60, B 50 minutes) before its last end |
| 2 | `rb/s03_desk_e193.sh` with `RB_GITLOCK`; **never inside the lab-git lock** | yes | yes | anything but 0: no box step that day; one exception: a pull whose output shows the upstream did not answer (step 2 again once it answers) |
| 4 | the look, `../q141k-runbook/k6/s05_look_k6.sh aifoundry3`, BEFORE the post | yes | yes | FREE; a holder: bounded polls (`--wait`), at most 30 minutes, else no sitting that day |
| 3 | the day's post (the card lane's), or the owner's waiver recorded | once a day | (the day's post covers it, or its rewrite) | the post's id and text in the lane's result, or the waiver's words |
| 5 | `rb/s07_a3_sync_e193.sh` | yes | yes | 10: a session or runbook job of ours on the box; 16: uncommitted synced paths or a file off its sha256 |
| 6 | `rb/s08_a3_build_e193.sh start`, then `wait` while it says 17 | start + wait | `wait` only on A's day (it reads the day's build); start + wait on a later day | 0: RB_OUT/e193-built.txt (X04-BUILT: BODIES CHECK PASS, HOST-BEHAVIOUR OK, LISTING SAME x3); 16: rebuild once (two starts a Pacific day at most); a third start: NO-THIRD-BUILD, no sitting today; a 14 on wait: no reading, wait again |
| 7 | `../q141k-runbook/k6/s09_a3_reads_k6.sh` | yes | yes | k6's (TDP 0 W / 65 C / 600 MHz; et-who clean) |
| 8 | `rb/s10_a3_dry_e193.sh start`, then `wait` | yes | yes | 0 (the session with DRY=1 on the box; both listings SAME) |
| 9 | `rb/s11_a3_session_e193.sh <A\|B>` | `A` | `B` | 0 launched (its "rest:" line in the runbook log); 10 refused (the rest, a session or job of ours, no dry pass or build today, this sitting's smoke gate failed today, for B no sitting A or a crashed sitting A): read why, never around it |
| 10 | `rb/s20_wait_e193.sh <A\|B>`, again while it says 17 | `A` | `B` | 0: ended, its manifest written ("main run ended at a registered stop" when a stop or the deadline ended it: the passes done stand); 16: a gate stop before the main run (GATE-STOPPED), or a crash of the main run (MAIN-CRASHED: no registered stop), either still collected (section 3); 14: gone without "session end" (read the box read-only) |
| 11 | `rb/s22_collect_e193.sh <A\|B>` (after the post's release, if a post was made) | `A` | `B` | 0 COLLECTED, into the sitting's data directory, or, for a sitting that ended at a gate, into its gate stop's record (`docs/reports/gate-stops/<day>-e193-x04-clock-sitting-<a\|b>-T<T0>-aifoundry3/`); 16: COPY-BACK not exact, the scrub, the desk-path gate (E183 note 5), the history check, or a session log that does not say clearly how it ended: commit nothing, read why |
| 12 | the commit of what step 11 collected, after the public-text scan, through the lab's commit script, new files only: the data directory `docs/reports/data/<day>-e193-x04-clock-sitting-<a\|b>-aifoundry3/` with its README in [DATA-README-FORM-e193.md](DATA-README-FORM-e193.md)'s form (results first, registered against happened, departures dated); or the gate stop's record with that file's gate-stop form | yes | yes | |
| 13 | after the data commit only, never on a gate stop's record: `rb/s24_reduce_e193.sh <A\|B>` | `A` | `B` | the registered reducer (unchanged) and the checker: RB_OUT/x04-e193-<sitting>.json, checks-e193-<sitting>.json; the records lane commits them beside the data; after a crash, only once a dated note says the passes are reduced |

**To stop a sitting by hand** (the operator's stop, a registered stop): touch the running runner call's own stop file,
`build/e193/T<T0>/smoke/STOP` during the smoke or `build/e193/T<T0>/x04/STOP` during the main run (the runner checks it before every run
and ends there), and `build/e193/T<T0>/STOP` (the session then starts nothing more). Never kill a process: the runner ends its own device
process and stops its sampler.

## 3. After a gate stop, a registered stop, or a crash (fix-e193)

- **A gate stop** (`GATE-STOP:` in the session log: a gate before the sampler, the start config, the operator's stop before the main run,
  the smoke gate; session.rc 3; no main run) is **no sitting: no data** (E193.md 11). Step 11 still collects it (E184's lesson), into its
  **gate stop's record** under `docs/reports/gate-stops/`, never under `docs/reports/data/`: step 2 reads every `docs/reports/data/*e193*`
  path as an E193 datum, so a gate stop committed there would refuse every later try of sitting A, and step 9 would refuse sitting B
  (verify-e193's finding 2). Commit the record (new files only, its README in the gate-stop form); it is never reduced. **The sitting is
  then tried again with no amendment** (no pass of it ran): after a gate before the sampler, once the gate has cleared, with the
  40-minute rest after any session of ours that opened the card (step 9 reads it; a session that opened no device is skipped); after the
  smoke gate, **not the same day** (E193.md 11: "no sitting that day"; step 9 refuses). A try on a later day needs the owner's go for that
  day (section 1).
- **A registered stop, the deadline or the cap** (`main run stopped: ...`; session.rc 1): the passes done stand and are reduced as they
  stand (E193.md 6 and 11); the data directory is committed; the missing passes are never re-run without a dated amendment (step 2 then
  refuses another sitting A); sitting B follows on its own rest.
- **A crash** (`main run ended without a registered stop: ...`: the runner exited non-zero with no stop recorded, a traceback for one;
  session.rc 4; step 10 says MAIN-CRASHED and 16) is **not a registered stop**, and E193.md 11 has no row for it (verify-e193's finding 5):
  **report it, kill nothing** (the runner's own clean-up stops its sampler; the session makes its closing read), collect it into its data
  directory and commit those records, then stop the day. **A dated note decides whether its passes are reduced**, and no further sitting
  runs before that note: step 13 waits for it, and step 9 refuses sitting B after a crashed sitting A.
- **No sitting, no data:** a gate stop's record holds no datum and no price; a crash's records hold data whose use a dated note decides.

## 4. Never

- No step 2 but `rb/s03_desk_e193.sh`, and never inside the lab-git lock; no box step without step 2's 0 that day; no step out of the
  order above; never step 5, 6 or 8 while a session of ours runs (they refuse); never sitting B before sitting A (step 9 refuses).
- **No change to an arm, a value, the order, a window, a threshold, a stop, a cap or the reduction** except by a dated amendment before
  the data (E193.md 17); no pass re-run after a stop or the deadline without one; the runner and the reducer only at their registered
  sha256 (`run_x04.py` `26d08862...` and `reduce_x04.py` `98bbc174...`, in the registration's list).
- No device command but the kit's READs (dmcmd_audit GO): no set, no reset, no governor, TDP, threshold, clock, voltage, fan or firmware
  change; no statistics reset (`--reset-ms`); no firmware-revisions query; no PMIC command; no power cycle and nothing that risks one;
  never command 74 (the per-sensor codes are not recorded: E193.md 4); never kill a device process.
- Never two sessions of ours on aifoundry3 at once; never beside another user's process or holder (the session's holder check and the
  runner's before every block refuse); never on two cards (the runner and the host refuse a host with more than one ops node).
- Never a lab user's login in any file (the collection's scrub masks every holder line's user and our own login, and refuses any
  /home/ path left); never a forecast number of E193's sealed forecasts in any lab file, and no scoring against them (the model session
  scores them privately after the data commit).
- Never touch another run's files on the box: E193 writes only E193's root (`build/claims-v3/aifoundry3/e193`), `build/e193/` and the
  runbook's own `build/q141k/` entries.
- Never run the reduction before the data commit, nor on a data directory that is not committed and clean.
- Never a card reset (E193.md 9: a launch that did not finish may leave a hung hart, which needs one; that is never this run's to make:
  stop, keep the records, report to the owner and the lab admin).

## 5. Labels

Every figure here is **registered** (E193.md) or a **desk check of code** (KIT.md). Nothing here is measured, blind, held out or post hoc.

SPDX-License-Identifier: Apache-2.0
