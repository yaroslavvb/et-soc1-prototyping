# E194's card-lane brief: what the lane that runs E194 on aifoundry2's own card 0 does, in order, from aifoundry2 itself, and what it never does (Q183; kitted, not run)

*Sun 15 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q183, lane `kit-e194`; fixed by lane `fix-e194` after E194's verifier, the same
day, before any E194 datum: KIT.md section 11), beside [KIT.md](KIT.md); written after E194's registration ([E194.md](E194.md), its list
`SHA256SUMS-e194-registration` sha256 `788af7da...`, 17 entries, and its dated note 1, `E194.md.dated-note-1.md`) and before any E194 datum.
No card was claimed or opened, no device command was sent, no other lab box was reached, nothing was posted. This brief changes no forecast,
band, rule, threshold, K, order, plan, cap or registered stop line.*

## 1. What the go must carry (E194.md 13)

- **The owner's go naming E194 on aifoundry2 card 0, under its governor as found (800 MHz under load; nothing set), reads only**, about **95
  card-minutes (cap 110)**; **the host's package counter not read** (default no: step 9 runs without `--rapl-allowed`); **the post: none**,
  by his standing waiver ("don't worry about discord post, just use the machines, nobody is using them", Sun 15 Nov 2026 10:22:36 PST),
  recorded in the result and the data README in those words.
- **THE REBOOT GATE: CLOSED TODAY, and the go must answer it.** aifoundry2 booted **2026-11-13 16:53:28 PST** (after it went down that
  afternoon), **after E69's firmware read of record, 2026-10-27 13:56:26 PDT**. The go checklist's rule (k6's `rb_guard_text`, "fault 12")
  refuses every launch on aifoundry2 booted after that read (IDENTITY-STOP, step 9 exits 16) and the look reads 16; the firmware build is
  carried by uptime continuity only, never by the firmware-revisions query. No READ path in this kit shows the firmware build: the config
  read's identity block names the node, the device ID and the TDP but no firmware build (E190 arm A's committed `config-start.err`), and
  this boot's kernel log names the driver and the PCI device but no firmware build (a desk read, KIT.md section 8). **So no E194 session can
  launch until the owner rules how the firmware identity is carried across that reboot** (a dated amendment before step 4: a READ-path
  identity he and the field manual's owner accept, or the rule's exception for this box); the kit does not loosen the gate.
- **THE IDENTITY GATE** is part of the session: the start config read's stderr must name `/dev/et0_mgmt` and device ID 0 alone with
  minion_mv between 450 and 600, and et-who with the sampler running must show our lines on card 0 only; either failing ends the session
  before any launch (a gate: no data, never a failed prediction).
- **One session of ours on aifoundry2's card at a time** (the booking key `aifoundry2`), and **THE QUIET DESK FLAG** for the span from the
  look to the copy-back (section 2, steps Q and Q').
- **The window from the go at G**: last start G+1:30, last end G+3:30, each rounded UP to the whole minute, inside one Pacific day. The
  session needs its 110 card-minutes (6,600 s) before the last end at its launch, after about 30 minutes of box steps; about 15 minutes of
  collection follow.
- **The rest:** E194's first card command at least 40 minutes after our last real session on this card (E190 arm A's, Fri 13 Nov 2026,
  ended 16:24:57 PST, is the last one today). Step 7 reads it before its config read and step 9 before its launch, and each refuses (10)
  before that.
- **The anchor lines** the go names (the kit's LAND.md gives them with the landed commit): E194's registration and kit commits ancestors of
  HEAD; the registration's list `788af7da...` (17 of 17 OK), E194.md `a8ed7f50...` and its dated note 1's list `SHA256SUMS-e194-note1`
  (1 of 1 OK); the kit's list `SHA256SUMS-e194-kit` and step 2 (`rb/s03_desk_e194.sh`, outside that list) at their stated sha256, every
  entry OK; no E194 datum in any ref. E191's second session's data folder (`...-aifoundry1-c1-s2/`) in main is expected and does not stop
  step 2 (fix-e194: both of E191's folders are left out of the never-run check).

## 2. The steps, in order (paths under `tools/claims-v3/e194/`; run from the lab clone's top on aifoundry2)

Setup: `RB_OUT` a new directory outside the repo (E194's own), `RB_LOCK` the round's lock file of checks, `RB_GITLOCK` the lab-git lock,
`RB_QUIET` the round's quiet-desk flag file for aifoundry2, **`RB_QUIET=W/locks/quiet-desk-aifoundry2`** (outside the repo: the very file the
round's other lanes read before they start a device-named process or a session script on this box; fix-e194, verify-e194's nit 8);
`PATH` with the round's GNU date shim; git reads over HTTPS by
the round's environment-only rewrite. k6's drivers bound every box call; the box is this machine, reached by ssh to itself as E190 arm A's
day reached it. **A printed login link stops the step (11) and appends `<HH:MM:SS> aifoundry2 needs a check` to `RB_LOCK`:** nothing is
retried. Nothing in these steps opens the card but steps 7 and 9 (and the session step 9 starts).

| # | the step | what to do with its exit |
|---|---|---|
| B | `bash W/book.sh take aifoundry2 <lane>` | 1 = another lane holds the box: stop |
| 0 | THE LOAD RULE (`uptime`: the 1-minute load below 8, else wait in bounded chunks until below 6); then `bash W/slot.sh /usr/bin/flock -w 600 -E 76 $RB_GITLOCK /usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v2.py tree --pull` (`-E 76` inside slot.sh, never 75), which must print DAY2-CHECK-V2 OK; then E194's anchor lines exactly as LAND.md states them; helper scripts take the weekday from the clock | any line not as stated: no box step that day |
| H | `bash W/hold.sh add <lane>`; LAB's status reads 0 lines | else remove the hold, release the booking, stop |
| 1 | `rb/s02_window_e194.sh <YYYY-MM-DD> <last start> <last end>` | first; today's day only |
| 2 | `rb/s03_desk_e194.sh` with `RB_GITLOCK` set, under slot.sh, THE LOAD RULE first; **never inside the lab-git lock** | anything but 0: no box step that day (one exception: a pull whose upstream did not answer: run once more when `git ls-remote origin` answers) |
| Q | **THE QUIET DESK FLAG, raised right before the look:** `bash rb/quiet_e194.sh raise <lane>`, then `bash rb/quiet_e194.sh count --wait` (THE P2 COUNT: device-named processes and session or queue scripts of ours on this box, read again up to 5 times 2 s apart for our own live collector's read) | raise 10: another lane's flag is up: wait for it, never overwrite it; count 16: something of ours runs that the flag forbids: wait (bounded) or no session |
| 4 | the look, `rb/s05_look_e194.sh` | FREE; HELD (17): `--wait` polls, at most 30 minutes in all, else no E194 that day; **16: aifoundry2 booted after E69's firmware read of record: no launch (section 1)** |
| 3 | the post: none (the owner's standing waiver) | never a post |
| 5 | `rb/s07_tree_e194.sh pull` | 17: the box tree does not yet hold the kit commit (call again with pull); 10: a session or job of ours on the box; 16: E194's paths modified there or a file off its sha256 |
| 6 | `rb/s08_build_e194.sh start`, then `wait` while it says 17 (after a 14, "no reading": wait again) | 0: RB_OUT/e194-built.txt names what built; each kernel's line reads `KERNEL OK` (THE KERNEL GATE, the pins made on this box); 16 with neither built: start once more (at most two starts a Pacific day); a program not built is SKIPPED (no data) |
| 7 | `rb/s09_reads_e194.sh` | 0: card 0's config TDP 65 W / 65 C / 600 MHz, minion_mv between 450 and 600, /dev/et0_mgmt and ID 0 (a read, nothing set; its object read by `e194_common.py --config-line` from the read's stdout, kept on the box: fix-e194); **10: the rest has not opened (no config read was made): run it again after the rest opens**; 16 "no config read came back": our own live collector can hold the management node for a moment (it allows one opener): run step 4 again and, when it reads FREE, run this step ONCE more; a second such 16, or any other 16: no session |
| 8 | `rb/s10_dry_e194.sh start`, then `wait` | 0 with `E194-DRY rc=0 passes=n of n (each PASS with the clock ok) dry-check=1 identity-lines=2` |
| 9- | before step 9: read step 10's session reading (`ours_live "session_$RUN.sh"` with RUN=e194) against step 9's launch line (`setsid nohup bash tools/claims-v3/e194/session_e194.sh`): the same name | a mismatch: stop and report (E183's lesson) |
| 9 | `rb/s11_session_e194.sh FULL` (`--rapl-allowed` only on his go) | 0 launched (its rest line and its P2 count in the runbook log); 10 refused (the rest, the P2 count, a session or job of ours, no dry pass or build today): read why, never around it; **16 IDENTITY-STOP: the reboot gate (section 1): no launch** |
| 10 | `rb/s20_wait_e194.sh`, again while it says 17 | 0: ended with its manifest and **the runner exited 0** (runner.rc; a session whose queue a stop line, THE CLOCK RULE's second off-clock pass, the identity stop or THE EARLY STOP ended also reads 0, with its "STOP: ..." line among the lines printed); **16 "the runner exited <rc> after the session's end and stopped at no gate"** (fix-e194, verify-e194's finding 3: a runner fault after the gate, its finally block's "session end" and manifest written all the same): read runner.out (read-only), report it, then collect; 14 runner.rc not written: wait once more; 16 GATE-STOPPED (the box check, the lock, a holder or an unreadable et-who, the start config or THE IDENTITY GATE, the stop-path test, the smoke, or an early stop at the gate): collect it; **16 BOUND-SEEN: a host outlived the runner's 30 s bound: report it at once, kill nothing, keep the booking.** Read each pass's words (PASS, SHORT k of K, FAILED RUN; the clock ok / off / unread; SET ASIDE: the clock: ...), any "the sampler is not live" line, any "the host's line reassembled" line (on this box's runtime none is expected: report each with its run.json `host_line`), and any "the host's line could not be read (...)" line (fix-e194: a span that is not a whole known runtime line, a foreign newline inside the line, a stale object, or a line that fails its command's checks read 'none': that pass is a FAILED RUN, never read around; report each with its `host_line`) |
| 11 | `rb/s22_collect_e194.sh` | 0 COLLECTED (COPY-BACK EXACT, THE BOX-TREE GATE, the reducer, the scrub, the desk-path gate, the history check; its last line names the runner's exit status, which the data README's "What ran" names too); 16: commit nothing, read why. Expect each pass's `reduced ...` line to read `ok False` with the reducer's clock line ("minion clock in busy samples: [600, 800] MHz ...") as its only hard line: the governor's climb lies inside the reducer's busy window, and E194.md 8.2 has THE CLOCK RULE read that line, never as a failure (the desk's end to end: every pass so). Any other hard line stands |
| Q' | **THE QUIET DESK FLAG lowered after the copy-back:** `bash rb/quiet_e194.sh lower <lane>` | |
| 12 | the data README from `rb/data-readme-form-e194.md` (results first, registered against happened, departures dated, its Files table against FILES.txt, the post's waiver in his words and its time), `rb/readme_check_e194.py <data dir>` (README-CHECK-E194 OK), the public-text scan (the reducer's note "RAPL is root-only" in every energy.json is expected: keep it, name it), then `LAB_QUIET_HOLD_OWNER=<lane> bash W/commit_lab.sh "<subject>" "<body>" docs/reports/data/<day>-e194-blind-day-aifoundry2` | it must print "COMMIT_LAB: pushed <sha>"; on exit 5 or 6 run it again |
| 13 | after the data commit only: `rb/s24_score_e194.sh` | it exits 0 whatever the words: READ the four rules' words (E194-S1, S1T, S2, S2T) and RB_OUT/scores-e194.json; a FAIL is reported as FAIL; fewer than 2 good passes is NO DATA; a records lane commits scores-e194.json |
| E | `bash W/hold.sh remove <lane>`; `bash W/book.sh release aifoundry2 <lane>`; the quiet desk flag lowered | on every stop path too, after the last step that ran (a BOUND: keep the booking until the orchestrator says) |

### THE EARLY STOP (the only levers, both graceful)

To end a running session early (his word, a hazard, the window's last end too close): **write the stop file** into the session's own
directory, on this box: `touch ~/claude/et-soc1-prototyping/build/e194/T$(cat "$RB_OUT/e194-T0.txt")/STOP`. The runner reads it before every
start and every 0.2 s while idle: no further process starts, the running host (if any) ends by itself and keeps its idle after, then the
closing runs (the closing config read, queue.json with `early_stop`, "session end", the lock released, MANIFEST.sha256 last); asked for at
the gate it ends the session there in its own words (16), never "stop-path test failed". A **SIGTERM to the runner's own process** (the one
whose command line runs `tools/claims-v3/e194/run_e194.py session --t0 <T0>`; never `session_e194.sh`, never the process group) does the
same. Never SIGKILL, never a signal to a host or the sampler. Then step 10 (0) and step 11 as usual.

## 3. Never

- No step 2 but `rb/s03_desk_e194.sh`, and never inside the lab-git lock; no box step without step 2's 0 that day; no step out of the order
  above; never step 5, 6 or 8 while a session of ours runs on aifoundry2 (they refuse).
- **Never a launch past the reboot gate without the owner's dated ruling** (section 1); never the firmware-revisions query.
- **Never ET_DEVICES or V3_DEVICE set** for a device process on this box (the guard refuses them); never `dev_mngt_service` or `et-powertop`;
  never a node or lock of any other card.
- **Never a second session of ours on aifoundry2's card**; never a stand-in or real session, reader, `sys_emu`, built host or runbook desk
  test of ours on aifoundry2 while THE QUIET DESK FLAG is up; never overwrite or remove another lane's flag.
- No device command but the kit's READs (dmcmd_audit GO); no set, reset, governor, TDP, threshold or clock move; no statistics reset; no
  power cycle and nothing that risks one; never kill a device process (a BOUND line: report, kill nothing); an early stop only by the stop
  file or a SIGTERM to the runner's own process.
- No pass, smoke or anchor beyond the registered session (the counters arm is DROPPED); no re-drawn order; no K but the registered; no
  `--reset-ms`; the host's package counter only on his go.
- Never another user's process or session; never a lab user's login in any file (the collection's scrub replaces the box home and our
  login, and refuses any /home/ path or login left; THE BOX-TREE GATE refuses a desk path before anything is written).
- Never edit a collected file; never a post (his standing waiver).
- Never run the scorer before the data commit, nor on a data directory that is not committed and clean.

## 4. Labels

Every figure here is **registered** (E194.md) or a **desk check of code** (KIT.md), or a **desk read of committed records** (the boot
times, the firmware read of record, E190 arm A's session end). Nothing here is measured, blind, held out or post hoc.

SPDX-License-Identifier: Apache-2.0
