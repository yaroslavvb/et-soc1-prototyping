# E209's card lane brief: one session on aifoundry2 card 0 under its governor, run from aifoundry2 itself (Q202, lane kit-e209; kitted, not run)

*Tue 17 Nov 2026 (week 47), PST, desk only, beside [KIT.md](KIT.md), in E200's brief's form (`tools/claims-v3/e200/CARD-LANE-BRIEF.md`: the box
that is the desk, THE QUIET DESK FLAG, the reboot gate) with E207's step table for the blind matmul day (`tools/claims-v3/e207/CARD-LANE-BRIEF.md`:
THE ONE-LAB RULE, THE QUIET HOLD, step 6n). **The card day:** Tue 17 Nov 2026 or a later day, G the card lane's booking of aifoundry2 that day.
This is a desk statement for the card lane and the readiness check, never the owner's go. Every step below is a committed script run from the
lab clone's top, each as one plain call from a script file (no `bash -c`, no background `&`), with k6's exit codes: 0 done; 10 refused; 13 past
a bound; 14 a call failed; 15 a holder; 16 a gate says stop; 17 call again. Paths are under `tools/claims-v3/e209/` unless named. Before the
land, Q202c's lane `fix-e209` answered the adversarial verifier's findings (verify-e209): the rows of steps 0, 2, 6n, 11, 13 and E below,
section 3's LEFTOVER line, E209.md's amendment A1 and KIT.md section 11.*

## 1. What the go carries (E209.md 6: the owner's standing words, the registration's items as defaults)

- **G1.** E209 on aifoundry2 card 0 under its own governor as found (each process from the 600 MHz boot point; 600 / 700 / 800 MHz; TDP 65 W,
  threshold 65 C, power state 3 at the start config gate), **reads only** (dmcmd_audit_v2 GO: 12 send sites, every one a READ, fwgate's one
  firmware-revisions read among them by the owner's rulings of 15:07:01 and 15:09:49 PST Sun 15 Nov 2026), **nothing set**; one session of
  ours on aifoundry2 at a time.
- **G2. The session (E209.md 3 and 6):** the smoke (E208's three smoke arms, 2 s each), A1, N1, pass 1 (the 45 points in the registered shuffle,
  A2-A4 after the 12th, 24th and 36th), pass 2 (the ten doubled points reversed), A5, N2: **62 runs**, each a burst (one 6 s process) or, at
  e39 and e43, three processes back to back; **28.7 card-minutes planned**; no run starts after 45 card-minutes, the session ends at 55. Cut
  short, the registered subset is the smoke, A1, N1 and pass 1 with its anchors (every point once, 23.7 card-minutes).
- **G3. The rest (E209.md 6):** the first card command at least 40 minutes after the last session on aifoundry2 card 0 ended, whoever ran it (the
  model session's a2c0-S1r ended 00:10:41 PST Tue 17 Nov 2026; any later session counts: step 7's rest rule reads the lab's committed data,
  the round's release records and the box root).
- **G4. The window:** G = the booking; last start G + 1:30, last end G + 3:30, each rounded up to the whole minute, inside the Pacific day; G
  at 20:29:00 PST or earlier.
- **G5. The post: none,** the owner's standing waiver (his words, Sun 15 Nov 2026 10:22:36 PST: "don't worry about discord post, just use the
  machines, nobody is using them"), unless his go names one.
- **G6. The host's package counter: NOT READ.**
- **The freeze line** is MM1-v2's forecasts, pushed in `3ca4b717` at 01:44:48 PST Tue 17 Nov 2026 (E209.md 0); step 2 checks it and prints it.
  No sealed forecast of the model session was posted for E209 when this kit was written; one posted before the first card command is
  registered in `tools/claims-v3/sealed-e209/e209-freeze-lines.md` by a desk lane BEFORE the booking (step 2 refuses while the round's record
  `W/out/orch/sealed-e209.txt` lists a sha256, on a line that is not a comment, that the note does not register: the E206 lesson); it stays
  sealed (no number of it in any lab file).
- **Claims:** while `W/out/orch/claim-aifoundry2.txt` stands (the model session holds the box), the queue reads CANCELLED: no step at all.

## 2. Setup and the order of the steps

    W=<the round's workflow folder>; LAB=<the shared lab clone>; LANE=card-e209
    mkdir $W/out/$LANE/rb-e209 and $W/out/$LANE/box-e209      (new and empty: E209's own RB_OUT and box root)
    export RB_OUT=$W/out/$LANE/rb-e209 E209_ROOT=$W/out/$LANE/box-e209 RB_QUIET=$W/locks/quiet-desk-aifoundry2 RB_LANE=$LANE
           RB_RELEASES=$W/out/orch/e208-releases.txt:$W/out/orch/e212-releases.txt RB_ROUND_OUT=$W/out RB_W=$W
           RB_GITLOCK=$W/locks/lab-git.lock RB_SEALED=$W/out/orch/sealed-e209.txt
    <GH> = the round's environment-only HTTPS rewrite for git reads (never a config file)
    NEVER set RB_DESKTEST, RB_FWGATE, RB_GITHUB, RB_HOME_WORK, RB_NOW, RB_DATA_LAB, RB_E209_KITPIN, E209_DESKTEST, E209_FIRST_MAX_S, MMS_FAKE_*
    or E209_SI_*: they are the desk tests' (each step refuses the RB_ ones outside a desk test; start_e209.sh marks a session DESKTEST when
    E209_DESKTEST takes a desk record, and the collection refuses such a session)

**THE ORDER: B, D+, 0, H, 1, 2, D-; Q (the quiet desk flag); 4 the look, 5 the sync, 6 the build, 8 the dry pass, 6n the never-run search;
then, once the rest has opened and within 30 minutes of 6n, 7 the reads and 9 the launch, back to back; 10, 4', C+, 11 (with Q-), 12, C-, 13,
E.** Step 7 sends the day's first card command only when fwgate's look reads NEEDS-READ (its one firmware-revisions read, a READ); when the
look reads CONTINUITY it sends nothing and the session's own config read (step 9) is the first card command. Steps 0-6, 8 and 6n send nothing to
the card (the look reads fwgate's records, et-who and ps; the sync copies files; the build runs the host only to its refusals before the device
layer; the dry pass opens no node; 6n reads files). Step 9 refuses more than 120 s after step 7's stamp.

| step | call | expected | any other exit |
|---|---|---|---|
| B | `python3 $W/out/orch/queue_state.py aifoundry2 <the round's experiments before E209>` (QUEUE OVER), THE DAY, then `bash $W/book.sh take aifoundry2 $LANE` | BOOKED; G = this moment | CANCELLED (a claim): SKIPPED; busy: no step at all; stop |
| D+ | `bash $W/onelab.sh desk $LANE` (THE ONE-LAB RULE, right before step 0) | ONELAB: in its desk span | 3: call again (each call waits at most 9 minutes) |
| 0 | `uptime` (THE LOAD RULE: at most 8); GitHub main read (<GH>); the land's anchor lines at LAB's HEAD (the registration's and the kit's land records, `LAND.md` of each, as the land lane re-read them at the landed commits), **step 2's own sha256 among them**; any sealed E209 forecast registered first | as stated | no step that day: D-, E |
| H | `bash $W/hold.sh add $LANE`; `git -C $LAB status --porcelain --untracked-files=all` | 0 lines | D-, E |
| 1 | `bash rb/s02_window_e209.sh <G epoch>` | "the window written to RB_OUT/window.env" | 10: D-, E |
| 2 | FIRST `sha256sum rb/s03_desk_e209.sh` at LAB's HEAD equals the step-2 anchor line of the kit's land record (nothing in HEAD pins step 2: it sits outside the kit's list so that it can pin that list; verify-e209's finding 4); then `env <GH> bash $W/slot.sh bash rb/s03_desk_e209.sh` (NEVER inside the lab-git lock; RB_W and RB_LANE set: outside a desk test it refuses unless D+ holds the lane's desk span) | "STEP2 PASS (HEAD <sha>)" | a different sha256: step 2 is not run: D-, E, tell the orchestrator; 17: again; 10: D-, E (read RB_OUT/step2.txt) |
| D- | `bash $W/onelab.sh undesk $LANE` (right after step 2, and on every stop path from D+ to here) | left its desk span | |
| Q | `bash rb/quiet_e209.sh raise $LANE`, then `bash rb/quiet_e209.sh count --wait` (THE P2 COUNT 0) | raised (one line `card-e209 <time>`); P2 0 | raise 10 (another's flag up: the model session's): wait in bounded chunks, never overwrite; count 17: again |
| 4 | `bash rb/s05_look_e209.sh [--wait]` | 0 FREE; the reboot gate CONTINUITY or NEEDS-READ | 17 or 15: again with --wait (30 minutes in all), then E; 16 (fwgate STOPPED or NO-RECORD): no session on this boot, report, Q-, E |
| 3 | the post: waived (G5) | | |
| 5 | `bash rb/s07_sync_e209.sh` | SYNCED: 72 files at the harness's sha256 | 10 (a session, build or dry pass of the kit runs in the box root): read why; 14: again |
| 6 | `bash rb/s08_build_e209.sh start`, then `bash rb/s08_build_e209.sh wait` while 17 | "MMS-BUILT: the kernel at E136's pin; the record of today ..." | 16: start once more (two starts a day at most; a third is refused: no session that day) |
| 8 | `bash rb/s10_dry_e209.sh start`, then `bash rb/s10_dry_e209.sh wait` while 17 | "DRY PASS" (62 of 62 runs in the registered order, every device call printed) | 16: no session that day; read RB_OUT/dry.out |
| 6n | `bash $W/slot.sh bash rb/s06n_neverrun_e209.sh` | its NEVER-RUN line (REPORTED, never a gate) | 14: again. A point found RAN BEFORE goes into a dated note before the data commit. **Other cards, REPORTED only** (verify-e209's finding 9; every one after MM1-v2's freeze, none on this card): E207 ran on aifoundry3 card 0 on Tue 17 Nov 2026 (07:06-07:53 PST, data 867f6a3f; 14 of E209's 29 shapes and its 8 shared points, verify-e209's count), E212's aifoundry1 sessions ran 6 of its shapes, and E206 ran e30's shape (aifoundry3 and aifoundry1 card 1); the scanner counts card-e207's own never-run scan files (its RB_OUT) as other-card hits and classes data-e212's session copies as desk files: the dated note names the other-card runs by experiment, and no rule changes |
| - | WAIT until the rest has opened (40 minutes after the last session on aifoundry2 card 0 ended); if 6n is then more than 30 minutes old, run 6n again | | |
| 7 | `bash rb/s09_reads_e209.sh` | "the first card command stamped ... (read or continuity; first/<FIRST>): step 9 within 120 s" | 17 "REST NOT OPEN until ...": wait, call again (nothing was sent); 15: the card not free: look again; 16 (fwgate's read DIFFERENT or UNREADABLE, its guard not ok, or a rest source unreadable): no session on this boot, report, Q-, E; 10: read why, never go around it |
| 9 | `bash rb/s11_session_e209.sh` AT ONCE | "STARTED <T0>-a2c0-E209" | 10 "more than 120 s": step 7 again (the stamp is set aside; fwgate reads once more only if its look says so); 16 IDENTITY-STOP: no session on this boot, report; 17: again |
| 10 | `bash rb/s20_wait_e209.sh` while 17 | 0 ENDED, runner rc 0 | 16: read its words (section 3: a gate stop, a LEFTOVER, GONE); 14: again |
| 4' | the look after: `bash rb/s05_look_e209.sh` once the session has ended | 0 FREE: nothing of ours holds the card | 15: read who holds it, read-only; a holder of ours after the session's end is a finding: write it up, kill nothing |
| C+ | `bash $W/onelab.sh collect $LANE` (right before step 11, at least 10 minutes before the last end) | in its collect span | 3: call again |
| 11 | `bash $W/slot.sh bash rb/s22_collect_e209.sh` (outside a desk test it refuses unless C+ holds the lane's collect span) | "DATA DIR docs/reports/data/<day>-e209-blind-matmul-aifoundry2 written; THE QUIET DESK FLAG lowered after the copy-back" | 14 (COPY-BACK NOT EXACT): read why, never by hand; 16 (THE SCRUB): nothing written in LAB, Q-, C-, E, tell the orchestrator; 10: read why ("not in its collect span": C+ first) |
| Q- | done by step 11 after the copy-back (`bash rb/quiet_e209.sh lower $LANE`); on every stop path after Q | lowered | 10: the flag is not ours: leave it |
| 12 | the README's dated notes (section 2 of its form: every departure, stop, gate, dropped run, the never-run report); the public-text scan; `LAB_QUIET_HOLD_OWNER=$LANE bash $W/commit_lab.sh "<subject>" "<body>" <the data directory>` | "COMMIT_LAB: pushed <sha>" | 5 or 6: run it again |
| C- | `bash $W/onelab.sh uncollect $LANE` (right after the push, and on every stop path from C+ to here) | | |
| 13 | `bash $W/slot.sh bash rb/s24_score_e209.sh` (after the data commit only) | the reducer rc 0, "LABELS OK" (when a labels file exists), the frozen scorer's words, then the readings beside them (E209.md A1, REPORTED: the points NO DATA named, reading (f)'s day offset, H4n on H4's line); outputs in RB_OUT/score/ only | 10: the data is not committed, or a label names no point or time case (correct the dated note and RB_OUT/ranbefore-e209.json, never the scorer; then 13 again); 14: read why. A later lane commits the outputs byte for byte and names the NO DATA points in its note |
| E | `bash rb/end_e209.sh` on every path's end, after the last step that ran: it lowers the flag if it is the card lane's, leaves its desk or collect span if one stands, removes the hold line and releases the booking if they are the lane's | "E: ..." each action named | 17: a session of ours still runs, a device-named process of ours is alive, or a session's `queue.json` records an unresolved leftover: nothing is released (step 10 waits; on a LEFTOVER the booking, the hold and the flag stay until the orchestrator clears them) |

## 3. Stop paths (each ends with E; nothing is ever killed)

- **Every stop path clears its flags first** (rb/end_e209.sh does it in order, each by its own tool, and never touches another's): D- inside
  D+..D-; Q- after Q (any stop from the look to the copy-back; a session that ran is collected first); C- inside C+..C-. A flag left behind blocks
  the other lanes' commits, collections, desk spans and desk tests.
- **Before the session** (B busy or cancelled; step 0; H; step 1; step 2's 10; step 4's 15 or 16; steps 5, 6, 8: refused or failed; step 7's
  10, 15 or 16): no session that day: no data, never a failed check.
- **THE REBOOT GATE stops** (step 4 or 7: fwgate's look STOPPED or NO-RECORD; step 7: its read DIFFERENT or UNREADABLE; step 7 or 9: its guard
  IDENTITY-STOP): no E209 session on this boot; nothing is retried (fwgate's ledger stops every later read, look and guard of this card for the
  boot); keep step 7's folder (`first/<FIRST>` in the box root) for the record and report to the orchestrator.
- **A gate stop of the session that never reached the card** (step 10's 16 with queue.json `t_first_ms` null: the box lock, the box check, the
  card's lock, a holder before the config read): no card command, no data; nothing is collected; the rest rule and "one session a day" never
  count it; once the cause has cleared, try again the same day in a NEW RB_OUT with the same G (steps 1, 2, the P2 count, 4, 8, 6n, 7, 9; the
  day's build in the box root stands) inside the window.
- **A gate stop after the session reached the card** (its config or identity gate, the identity read, the stop-path test, the smoke gate: runner
  rc 16 with `t_first_ms` set): collect it (step 11), say GATE-STOPPED in the README's dated note, commit it (step 12): it is the day's record,
  never reduced; a second session needs a dated amendment beside E209.md (step 2 refuses while an E209 data path exists).
- **A registered stop after the runs began** (a live stop line: the board above 85 W on 3 samples in a row, the shires' mean or a risen latch at
  or above 80 C; two failed processes in a row; the rule or the cap; the deadline; the operator's stop): the runs done stand as measured and are
  reduced as they stand (E209.md 7: a point with no run is NO DATA, never a failure); the missing runs are never re-run without a dated
  amendment.
- **A LEFTOVER** (a device process of ours alive past its TERM: step 10's 16 "ENDED with a LEFTOVER", or the RUNNING lines name one): KILL
  NOTHING, reset nothing, no PMIC or power action; the runner holds the card's lock until no device process of ours is left (at most 10
  minutes) and makes no closing read; keep the booking, the hold and the quiet desk flag as they are (rb/end_e209.sh refuses, 17, and releases
  nothing while a device-named process of ours is alive or the session's `queue.json` records the leftover unresolved: fix-e209); collect only
  once the leftover is resolved; write it up and escalate to the orchestrator and the owner.
- **A session that does not end, or a card that stops answering:** never kill a device process, never reset; keep the booking, the hold and the
  flag, write it up, escalate.
- **The operator's stop, by hand,** only if the owner asks or a reading calls for it: `bash $E209_ROOT/src/stop_mms.sh a2c0 <SID>` from a script
  file in the box root (E208's: it only touches the STOP files; the host ends at its next launch boundary, about 0.5 s; nothing is killed).

## 4. The window and the order on aifoundry2

From G (the card lane's booking of aifoundry2: `book.sh take` prints BOOKED): **last start G+1:30, last end G+3:30, each rounded up to the
whole minute, inside that Pacific day; G at 20:29:00 PST or earlier** (E209.md 6; step 1 refuses otherwise). Step 7 and step 9 refuse after
the last start; the session's deadline is the last end (start_e209.sh passes it to the runner); step 11 must start 10 minutes before the last
end.

| | example (desk arithmetic from the registered figures) |
|---|---|
| booked at 08:00:20 | `rb/s02_window_e209.sh <G>`: last start 09:31, last end 11:31; steps 2-8 and 6n about 15-25 minutes; step 7 as soon as the rest has opened (open since 00:50:41 unless a later session ran); the session about 29-33 minutes from its config read (rule 45, cap 55); collected and committed within about 30 minutes of its end |

**The order:** never two of ours on this card (book.sh key aifoundry2); E209's rest rule reads every session form of this card in the lab's
committed data (E208's, E194's, E200's), the round's release records (E208's and E212's) and the box root; E209's own session is E208's runner
form (queue.json `t_close_ms`, its `session end` line), so later rest rules read it too. The model session's E212 sessions on aifoundry2 come
after E209 (#11); while a claim of theirs stands, no step at all.

## 5. Never

- Never kill a device process: no SIGKILL, no `timeout -k`, no `kill -9`; never reset the card; no power cycle, no PMIC write, no firmware
  change, no OTA, no driver reload (the field manual's gates bind them; none is E209's).
- Never set anything: no governor, TDP, threshold, clock, voltage or fan; no statistics reset. The firmware-revisions query is a read (the owner's
  rulings of 15:07:01 and 15:09:49 PST, Sun 15 Nov 2026), sent only by fwgate's read, once a boot.
- Never send a card command before the rest has opened (step 7 reads the rest first and sends nothing until it has); never run step 9 more than
  120 s after step 7's stamp.
- Never two sessions of ours on this card; never a session outside its window; never a second E209 session after one that reached the card
  without a dated amendment.
- Never start, beside the session, a process of ours named like a device process or a session or queue script on this box: THE QUIET DESK
  FLAG is up from Q to the copy-back; THE P2 COUNT must read 0 at Q, the look, step 7 and step 9.
- Never run step 2 inside the lab-git lock; never edit, pull or commit in LAB by hand; commits only through commit_lab.sh.
- Never edit a committed file of E209 or E208 (the registration, the kit, E208's proposal copy): a change is a dated amendment or kit note
  beside it, committed before the data it touches.
- Never put a forecast number or a score in the data directory's README; never a lab user's login, a home path, a credential or a private
  page's number (the collection's scrub refuses the login, any home path and the box root's own path).
- On this box E209 writes only its box root (E209_ROOT), RB_OUT, fwgate's ledger (by fwgate itself) and, at step 11, its data directory in LAB.

## 6. Gaps the go should know (none blocks; each is the kit's registered behaviour or a reading the desk cannot make)

1. **The host on this card:** the desk built the real host and ran it only to its four refusals; E208 ran the same host source and kernel
   bytes on this card (three sessions); the host's own sha256 depends on the box root's path, so the gate is the kernel ELF's bytes (E136's
   pin) and the build record of the day, as in E208.
2. **The card time is counted from the session's own config read** (E208's runner, unchanged): when step 7 sends fwgate's one firmware read
   (NEEDS-READ), it precedes that config read by at most 120 s, so the card time from the day's first card command is the runner's count plus
   at most 2 minutes; the collection records step 7's stamp beside the runner's figures.
3. **The pace:** the desk's dry pass counted 32.23 card-minutes (fix-e209's re-run; 32.22 in the kit lane's) at the doubles' pace (unscaled) against the registered plan's 28.7 at E208's
   measured pace; the rule (45) and the cap (55) hold either.
4. **The checks are REPORTED:** E208's data checker C0-C8 runs at the collection; a cut or stopped session FAILs C1 or C2 honestly, never a gate.
5. **Our own live collector** can hold the management node for a moment at the free checks: step 7 re-reads up to three times while every holder
   line is a reader of ours on /dev/et0_mgmt; E208's runner re-reads once after 5 s; a collision there is a gate stop before the config read.
6. **fwgate's one read:** if its look reads NEEDS-READ (no committed record after this boot), step 7 reads the firmware once; anything but EQUAL
   stops E209 on this boot.

SPDX-License-Identifier: Apache-2.0
