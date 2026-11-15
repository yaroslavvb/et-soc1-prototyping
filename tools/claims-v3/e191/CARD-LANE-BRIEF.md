# E191's card-lane brief: what the lane that runs E191 on aifoundry1 card 1 does, in order, from aifoundry2, and what it never does (Q178; kitted, not run)

*Sat 14 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q178, lane `kit-e191`; changed in place before the land by lane `fix-e191k`
after the kit's verifier, verify-e191k, and by lane `fix-e191k2` (Q180, Sun 15 Nov 2026) after its second verifier, verify-e191k2),
beside [KIT.md](KIT.md); written after E189's data commit `fa9098c4` (20:34:12 PST), limited to
the kit's mechanics and stricter gates (E191's dated note 1, section 3). The registration is [E191.md](E191.md) (`300d76e4`) with [its
dated note 1](E191.md.dated-note-1.md) (`8c8f825f`). No card was claimed or opened, no device command was sent, no lab box was reached,
nothing was posted. No E191 datum exists. This brief changes no forecast, band, rule, threshold, K, order, plan, cap or registered stop
line.*

## 1. What the go must carry (E191.md 13, note 1)

- **The owner's go naming E191 on aifoundry1 card 1, at 600 MHz as found, reads only**, about **95 card-minutes (cap 110)**; whether a read
  of the host's package counter is allowed (default no: step 9 runs without `--rapl-allowed`); **the post route for that day** (he posts,
  an Intel session posts on his word, or he waives it: he waived Sat 14 Nov 2026's, "it's fine not to announce, the cards are unused").
- **THE IDENTITY GATE** (note 1, item 3) is part of the session: the start config read's stderr must name `/dev/et1_mgmt` and device ID 1
  with minion_mv below 510, and et-who with the sampler running must show our lines on card 1 only; either failing ends the session before
  any launch (a gate: no data, never a failed prediction).
- **Never two sessions of ours on aifoundry1**, either card: the booking is the whole box (`W/book.sh take aifoundry1 <lane>`), the look and
  the guard refuse beside any session of ours, and the runner's holder rule refuses a line of ours on card 0.
- **Nothing on card 0**: no step names card 0's node or lock; every device process carries ET_DEVICES=1; card 0's 75 W PMIC alarm trips on
  loads E191 never sends there.
- **The window from the go at G**: last start G+1:30, last end G+3:30, each rounded UP to the whole minute, inside one Pacific day (G at
  20:29 or earlier). The session needs its 110 card-minutes (6,600 s) before the last end at its launch, after about 30 minutes of box steps;
  about 15 minutes of collection follow.
- **The rest:** E191's first card command at least 40 minutes after our last real session on aifoundry1 (either card; every tree; E190 arm
  B's session of Fri 13 Nov 2026 among them). Step 9 reads it on the box and refuses (10) before that: wait and run step 9 again.
- **The anchor lines** the go names (the kit's LAND.md gives them with the landed commit): E191's registration, note 1 and kit commits
  ancestors of HEAD; the registration's subtree `766e2463...` and its list `e458fa82...` (11 of 11 OK); note 1's list `45ebe831...` (3 of 3);
  the kit's list `SHA256SUMS-e191-kit` and step 2 (`rb/s03_desk_e191.sh`, outside that list) at their stated sha256, every entry OK; no E191
  datum in any ref.

## 2. The steps, in order (paths under `tools/claims-v3/e191/`; run from the lab clone's top)

Setup: `RB_OUT` a new directory outside the repo (E191's own), `RB_LOCK` the round's lock file of checks, `RB_GITLOCK` the lab-git lock;
`PATH` with the round's GNU date shim; git reads over HTTPS by the round's environment-only rewrite (`GIT_CONFIG_COUNT=1` with
`url.https://github.com/.insteadOf` for GitHub's ssh form). k6's drivers bound every remote call. **A printed
login link stops the step (11) and appends `<HH:MM:SS> aifoundry1 needs a check` to `RB_LOCK`:** nothing is retried; a session detached on the
box keeps running. Nothing in these steps runs a built binary on aifoundry2 or opens its card.

| # | the step | what to do with its exit |
|---|---|---|
| B | `bash W/book.sh take aifoundry1 <lane>` | 1 = another lane holds the box: stop |
| 0 | THE LOAD RULE (`uptime`: the 1-minute load below 8, else wait in bounded chunks until below 6); then `bash W/slot.sh /usr/bin/flock -w 600 -E 76 $RB_GITLOCK /usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v2.py tree --pull` (use `-E 76` inside slot.sh, never 75: slot.sh reads 75 as "slot busy"), which must print DAY2-CHECK-V2 OK; then E191's anchor lines exactly as LAND.md states them; helper scripts take the weekday from the clock | any line not as stated: no box step that day |
| H | `bash W/hold.sh add <lane>`; LAB's status reads 0 lines | else remove the hold, release the booking, stop |
| 1 | `rb/s02_window_e191.sh <YYYY-MM-DD> <last start> <last end>` | first; today's day only |
| 2 | `rb/s03_desk_e191.sh` with `RB_GITLOCK` set, under slot.sh, THE LOAD RULE first; **never inside the lab-git lock** (it takes it itself; nested it reads 16) | anything but 0: no box step that day; one exception: a pull whose output shows the upstream did not answer (run once more when `git ls-remote origin` answers) |
| 4 | the look, `rb/s05_look_e191.sh` | FREE on both cards; HELD: `--wait` polls, at most 30 minutes in all, else no E191 that day; 16: aifoundry1 booted after E82's firmware read: no launch |
| 3 | the post: as that day's go says (made after the look reads FREE; or waived, recorded in the result and the data README) | never a second post |
| 5 | `rb/s07_a1_sync_e191.sh` | 10: a session or job of ours on the box; 16: uncommitted synced paths or a file off its sha256 |
| 6 | `rb/s08_a1_build_e191.sh start`, then `wait` while it says 17 (after a 14, "no reading": wait again) | 0: RB_OUT/e191-built.txt names what built; each kernel's line reads `KERNEL OK` (THE KERNEL GATE: its .text the registered one, and its whole ELF a pinned one, E189's or the "() 15.1.0" toolchain's, or its loadable identity, second form, the pinned one; KIT.md section 1); the runner's box check at step 9 refuses a kernel or host no longer at its build record's sha256; 16 with neither built: start once more (at most two starts a Pacific day); a program not built is SKIPPED (no data); a host refused by the ET_DEVICES reading is never run |
| 7 | `rb/s09_a1_reads_e191.sh` | 0: card 1's config TDP 65 W / 65 C / 600 MHz, minion_mv between 450 and 510, /dev/et1_mgmt and ID 1 (a read, nothing set); 16 "no config read came back": our own live collector can hold the management node for a moment (it allows one opener): run step 4 again and, when it reads FREE, run this step ONCE more; a second such 16, or any other 16 (not card 1's read): no session |
| 8 | `rb/s10_a1_dry_e191.sh start`, then `wait` | 0 with `E191-DRY rc=0 passes=n dry-check=1 identity-lines=2` |
| 9- | before step 9: read step 10's session reading (`ours_live "session_$RUN.sh"` with RUN=e191) against step 9's launch line (`setsid nohup bash tools/claims-v3/e191/session_e191.sh`): the same name | a mismatch: stop and report (E183's lesson) |
| 9 | `rb/s11_a1_session_e191.sh FULL` (`--rapl-allowed` only on his go) | 0 launched (its rest line in the runbook log); 10 refused (the rest, a session or job of ours, no dry pass or build today): read why, never around it; 16 IDENTITY-STOP: no launch |
| 10 | `rb/s20_wait_e191.sh`, again while it says 17 | 0: ended with its manifest (a session ended by THE EARLY STOP below reads so too: its "STOP: an early stop was asked for" line); 16 GATE-STOPPED (the box check, the lock, a holder or an unreadable et-who, the start config or THE IDENTITY GATE, the stop-path test, the smoke, or an early stop asked for at the gate: "an early stop was asked for (...) before / during the stop-path test: the gate, no launch", never read as a failed stop path): release (if posted), then collect; **16 BOUND-SEEN: a host outlived the runner's 30 s bound: report it at once, kill nothing, keep the booking.** The runner then keeps card 1's lock while that host runs, polling its end (nothing killed), and runs the closing config read only after it has ended; if it still runs at the end bound less the closing's share, the runner releases card 1's lock with it running and skips the closing read ("card 1's lock is released with it running"; queue.json `alive_at_close`): report that too, the booking kept until the orchestrator says. Read each pass's reading words (PASS, SHORT k of K, FAILED RUN) and any "the sampler is not live" line (a pass with no live sample just before its host starts no host: no data; a live sample carries board_w, minshire[0] and the clock), and any pass line flagged "the sampler was not live during this pass" (no live sample for 2 s or more inside that pass: report it with its run.json gap; the pass is kept and scored as registered, and the sampler is restarted before the next host) |
| 11 | the release (if that day's post was made: ` — released` appended, every word kept), then `rb/s22_collect_e191.sh` | 0 COLLECTED; 16: COPY-BACK not exact, the scrub, the desk-path gate or the history check: commit nothing, read why |
| 12 | the data README from `rb/data-readme-form-e191.md` (results first, registered against happened, departures dated, its Files table against FILES.txt), `rb/readme_check_e191.py <data dir>` (README-CHECK-E191 OK), the public-text scan (the unchanged reducer's note "RAPL is root-only" in every energy.json is expected: keep it as collected, name it), then `LAB_QUIET_HOLD_OWNER=<lane> bash W/commit_lab.sh "<subject>" "<body>" docs/reports/data/<day>-e191-blind-day-aifoundry1-c1` | it must print "COMMIT_LAB: pushed <sha>"; on exit 5 or 6 run it again |
| 13 | after the data commit only: `rb/s24_score_e191.sh` | it exits 0 whatever the words: READ the four rules' words (E191-S1, S1T, S2, S2T) in its "scored:" line and RB_OUT/scores-e191.json; a FAIL is reported as FAIL; fewer than 2 good passes is NO DATA; a records lane commits scores-e191.json |
| E | `bash W/hold.sh remove <lane>`; `bash W/book.sh release aifoundry1 <lane>` | on every stop path too, after the last step that ran (a BOUND: keep the booking until the orchestrator says) |

### THE EARLY STOP (the verifier's finding 5; the only levers, both graceful)

To end a running session early (his word, a hazard, the window's last end too close): **write the stop file** into the session's own
directory on the box, one bounded call, T0 from step 9's `RB_OUT/e191-T0.txt`:
`timeout 60 ssh -o BatchMode=yes -o ConnectTimeout=15 aifoundry1 "touch nekko/build/e191/T$(cat "$RB_OUT/e191-T0.txt")/STOP && echo STOP-WRITTEN"`
(a printed login link: stop, append `<HH:MM:SS> aifoundry1 needs a check` to `RB_LOCK`, nothing retried; the session then runs to its own
cap and window). The runner reads the file before every start and every 0.2 s while idle: no further process starts, the running host
(if any) ends by itself and keeps its idle after, then the closing runs as for a stop line (the closing config read, queue.json with
`early_stop`, "session end", the lock released, MANIFEST.sha256 last); asked for after the start config read and before the queue starts,
it ends the session at the gate in its own words ("... before / during the stop-path test: the gate, no launch", 16; fix-e191k2), never
"stop-path test failed". A **SIGTERM to the runner's own process** (the one whose command line
runs `tools/claims-v3/e191/run_e191.py session --t0 <T0>`; never the session wrapper `session_e191.sh`, never the process group) does the
same. Never SIGKILL, never a signal to a host or the sampler. Then
step 10 (0) and step 11 as usual: the passes done are collected and scored (E191.md 12).

## 3. Never

- No step 2 but `rb/s03_desk_e191.sh`, and never inside the lab-git lock; no box step without step 2's 0 that day; no step out of the order
  above; never step 5, 6 or 8 while a session of ours runs on aifoundry1 (they refuse).
- **Never anything on aifoundry1's card 0**: no command naming its node or lock; never ET_DEVICES unset or other than 1 for a device
  process; never `dev_mngt_service` or `et-powertop` (they ignore ET_DEVICES and open every card's management node).
- **Never two sessions of ours on aifoundry1** (either card), never beside another lane's booking of the box.
- No device command but the kit's READs (dmcmd_audit GO); no set, reset, governor, TDP, threshold or clock move; no statistics reset; no
  firmware query; no power cycle and nothing that risks one; never kill a device process (a BOUND line: report, kill nothing); an early
  stop only by the stop file or a SIGTERM to the runner's own process (above).
- No pass, smoke or anchor beyond the registered session (the counters arm is DROPPED); no re-drawn order; no K but the registered; no
  `--reset-ms`; the host's package counter only on his go, and only as our own user.
- Never another user's process or session; never a lab user's login in any file (the collection's scrub replaces the box home and our
  login, and refuses any /home/ path or login left).
- Never edit a collected file; never a second post; never edit a post of another day.
- Never run the scorer before the data commit, nor on a data directory that is not committed and clean.

## 4. Labels

Every figure here is **registered** (E191.md, its note 1) or a **desk check of code** (KIT.md). Nothing here is measured, blind, held out or
post hoc.

SPDX-License-Identifier: Apache-2.0
