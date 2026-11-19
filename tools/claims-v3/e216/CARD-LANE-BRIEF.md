# E216's card lane brief: one session on aifoundry2 card 0 under its governor, run from aifoundry2 itself (Q227, lane kit-e216; kitted, not run)

**fix-e216 (Q227, Thu 19 Nov 2026, before any E216 datum; verify-e216's findings; KIT.md section 12):**

- **THE CPU RULE's gate:** steps 7 and 9 refuse (17, nothing sent) while the host's 1-minute load is 6 or more: wait and call again.
- **S1:** step 0's S1 refuses (10) a sealed record that exists but cannot be read, and reads a seal in either case of hex.
- **The registration:** it carries Amendment 1 (`E216-amendment-1.md`): P1 needs 5 decided pairs, and the never-run reading is
  registered.
- **Step 13:** it also runs `report_e216.py`, Amendment 1's REPORTED readings.
- **The runbook desk test:** it reads its full count only in the kit's stand-in form. The committed-kit form skips P4-P6, P14 and P17
  (KIT.md section 12: the counts).
- **RB_LAUNCHED:** it must name the actual launch marker of any E215 run booked when this lane reaches O (section 2).

*Thu 19 Nov 2026 (week 47), PST, desk only, beside [KIT.md](KIT.md), in E209's brief's form (`tools/claims-v3/e209/CARD-LANE-BRIEF.md`: the box
that is the desk, THE QUIET DESK FLAG, the reboot gate, THE ONE-LAB RULE, THE QUIET HOLD, step 6n) with E209's kit note 1 (THE MASK, the order
of steps 4 and 5 on a new box root) and E215's lessons (step 2 never rewrites a registered file; the G block last; step 6n judged by each point's
own reading; the scrub tested on records that carry the box's home). **The card day:** Thu 19 Nov 2026 with G at 20:29:00 PST or earlier, or
Fri 20 Nov 2026 from 00:00:30 PST; G the card lane's booking of aifoundry2 that day. This is a desk statement for the card lane and the readiness
check, never the owner's go. Every step below is a committed script run from the lab clone's top, each as one plain call from a script file (no
`bash -c`, no background `&`), with k6's exit codes: 0 done; 10 refused; 13 past a bound; 14 a call failed; 15 a holder; 16 a gate says stop;
17 call again. Paths are under `tools/claims-v3/e216/` unless named.*

## 1. What the go carries (E216.md 6: the owner's standing words, the registration's items as defaults)

- **G1.** E216 on aifoundry2 card 0 under its own governor as found (each process from the 600 MHz boot point; 600 / 700 / 800 MHz; TDP 65 W,
  threshold 65 C, minion 600 MHz at rest, power state 3 at the start config gate), **reads only** (dmcmd_audit_v2 GO: 12 send sites, every one a
  READ, fwgate's one firmware-revisions read among them by the owner's rulings of 15:07:01 and 15:09:49 PST Sun 15 Nov 2026), **nothing set**;
  one session of ours on aifoundry2 at a time.
- **G2. The session (E216.md 6, plan-e216.json):** E208's three smoke arms (2 s each), A1, N1, pass 1 (36 points: F, Y and Gt, an anchor after
  the 12th, 24th and 36th), pass 2 (the 16 Y points reversed), A5, N2, then **THE G BLOCK LAST** (g07, g08, g09, g10, g03, g04, g05, g06, g02,
  g01: rgm136's gemmLnc branch on rgm211's host): **69 runs**, each a burst (one 6 s process); **29.85 card-minutes planned** (the desk's dry pass
  at the doubles' pace: about 34); no run starts after 45 card-minutes, the session ends at 55. Cut short, the registered subset is the smoke,
  A1, N1 and pass 1 with its anchors (about 18.67 card-minutes).
- **G3. The stops (E216.md 6, registered):** the board strictly above **70 W on 3 samples in a row**; the shires' mean at or above **70 C**; the
  hottest-sensor latch at or above **70 C once it has risen** in the session. **The line 64.0 W** (every run's planning peak under it). The die
  gate a run starts under: 55 C, waited at most 180 s.
- **G4. The rest:** the first card command at least 40 minutes after the last session on aifoundry2 card 0 ended, whoever ran it (the model
  session's E212 S3 re-run ended 16:23:09 PST Wed 18 Nov 2026; any later session counts: step 7's rest rule reads the lab's committed data,
  the round's release records and the box root).
- **G5. The window:** G = the booking; last start G + 1:30, last end G + 3:30, each rounded up to the whole minute, inside the Pacific day; G
  at 20:29:00 PST or earlier.
- **G6. The post: none,** the owner's standing waiver (his words, Sun 15 Nov 2026 10:22:36 PST: "don't worry about discord post, just use the
  machines, nobody is using them"), unless his go names one. **G7. The host's package counter: NOT READ.**
- **The freeze line** is E216's registration commit (the commit that added `E216.md`, its push: `W/out/q227-freeze-e216.txt`); step 2 checks
  it in HEAD and prints it. **Sealed forecasts:** none was posted for E216 when this kit was written; a sha256 the model session posts before the
  booking is registered in `tools/claims-v3/sealed-e216/e216-freeze-lines.md` by a desk lane BEFORE the booking (step 0's S1 and step 2's
  check 10 refuse while the round's record `W/out/orch/sealed-e216.txt` lists a sha256, on a line that is not a comment, that the note does not
  register: the E206 lesson); a later seal goes in a NEW note (`e216-freeze-lines-2.md`, ...) with its record line written as a COMMENT. It
  stays sealed (no number of it in any lab file).
- **Claims:** while `W/out/orch/claim-aifoundry2.txt` stands (the model session holds the box), the queue reads CANCELLED: no step at all.

## 2. Setup and the order of the steps

    W=<the round's workflow folder>; LAB=<the shared lab clone>; LANE=card-e216
    mkdir $W/out/$LANE/rb-e216 and $W/out/$LANE/box-e216      (new and empty: E216's own RB_OUT and box root)
    export RB_OUT=$W/out/$LANE/rb-e216 E216_ROOT=$W/out/$LANE/box-e216 RB_QUIET=$W/locks/quiet-desk-aifoundry2 RB_LANE=$LANE
           RB_RELEASES=$W/out/orch/e208-releases.txt:$W/out/orch/e212-releases.txt[:<any later aifoundry2 release record>]
           RB_ROUND_OUT=$W/out RB_W=$W RB_GITLOCK=$W/locks/lab-git.lock RB_SEALED=$W/out/orch/sealed-e216.txt
           RB_LAUNCHED=card-e215a=$W/out/card-e215a/rb-e215a/e215-T0-A.txt:card-e215b=$W/out/card-e215b/rb-e215b/e215-T0-B.txt
           (the ready lane confirms each marker path from the other card lanes' go lines; a booking of a card lane not named there is waited for)
           (fix-e216, verify-e216's F6: card-e215b's second booking, 13:21:36 PST Thu, writes its RB_OUT under a new name, so the marker above
           would never appear for that run; if an E215 card lane holds a booking when this lane reaches O, the ready lane names THAT run's
           actual launch marker here, from its go lines: names only, never a datum. THE ORDER's code is unchanged: unnamed, it waits)
    <GH> = the round's environment-only HTTPS rewrite for git reads (never a config file)
    THE CPU RULE: every numerical step (2, 6n, 11, 13) inside $W/slot.sh with OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
    NUMEXPR_NUM_THREADS=1; the host's 1-minute load under 6 through the session (wait in bounded chunks while it is above 6); fix-e216
    (verify-e216's F8): steps 7 and 9 now gate on it themselves (17 while the load is 6 or more: nothing sent; wait and call again), and the
    orchestrator keeps aifoundry2's other lanes light while the session runs
    NEVER set RB_DESKTEST, RB_FWGATE, RB_GITHUB, RB_HOME_WORK, RB_NOW, RB_DATA_LAB, RB_BOOKS, RB_LOAD, RB_E216_KITPIN, E216_DESKTEST, E216_FIRST_MAX_S,
    MMS_FAKE_*, E216_FAKE_* or E216_SI_*: they are the desk tests' (each step refuses the RB_ ones outside a desk test; start_e216.sh marks a
    session DESKTEST when E216_DESKTEST takes a desk record, and the collection refuses such a session)

**THE ORDER: B, D+, 0 (with S1), H, 1, 2, D-; O (THE ORDER: every other card lane of ours that holds a booking past its launch step), Q (the
quiet desk flag); 5 the sync, 4 the look, 6 the builds, 8 the dry pass, 6n the never-run search; then, once the rest has opened and within 30
minutes of 6n, 7 the reads and 9 the launch, back to back; 10, 4', C+, 11 (with Q-), 12, C-, 13, E.** Step 7 sends the day's first card command
only when fwgate's look reads NEEDS-READ (its one firmware-revisions read, a READ); when the look reads CONTINUITY it sends nothing and the
session's own config read (step 9) is the first card command. Steps 0-6, 8 and 6n send nothing to the card (the look reads fwgate's records,
et-who and ps; the sync copies files; the builds run the hosts only to their refusals before the device layer, rgm211's inside a bubblewrap
with no card node; the dry pass opens no node; 6n reads files). Step 9 refuses more than 120 s after step 7's stamp. **On this boot** (aifoundry2
booted 16:46:04 PST Tue 17 Nov 2026, after E209's read of the previous boot) fwgate's look is expected to read NEEDS-READ: one read at step 7.

| step | call | expected | any other exit |
|---|---|---|---|
| B | `python3 $W/out/orch/queue_state.py aifoundry2` (QUEUE OVER), THE REST and THE DAY, then `bash $W/book.sh take aifoundry2 $LANE` | BOOKED; G = this moment | CANCELLED (a claim): wait; BUSY (another lane or the orchestrator, e.g. a seal hold): wait; at most until 06:00 PST Fri 20 Nov 2026, then SKIPPED |
| D+ | `bash $W/onelab.sh desk $LANE` (THE ONE-LAB RULE, right before step 0) | ONELAB: in its desk span | 3: call again (each call waits at most 9 minutes) |
| 0 | `uptime` (THE LOAD RULE: at most 8); GitHub main read (<GH>); the land's anchor lines at LAB's HEAD (`W/out/q227-anchor-lines-e216.txt`), **step 2's own sha256 among them**; then **S1** `RB_SEALED=$W/out/orch/sealed-e216.txt bash rb/s00_sealed_e216.sh` | as stated; S1 "SEALED-E216: sealed k of k registered" | no step that day: D-, E, which releases the booking (a seal NOT REGISTERED, or a record that exists but cannot be read: S1 exits 10; no session that day; tell the orchestrator) |
| H | `bash $W/hold.sh add $LANE`; `git -C $LAB status --porcelain --untracked-files=all` | 0 lines | D-, E |
| 1 | `bash rb/s02_window_e216.sh <G epoch>` | "the window written to RB_OUT/window.env" | 10: D-, E |
| 2 | FIRST `sha256sum rb/s03_desk_e216.sh` at LAB's HEAD equals the step-2 anchor line of the kit's land record (nothing in HEAD pins step 2: it sits outside the kit's list so that it can pin that list); then `env <GH> bash $W/slot.sh bash rb/s03_desk_e216.sh` (NEVER inside the lab-git lock; RB_W and RB_LANE set: outside a desk test it refuses unless D+ holds the lane's desk span). **It runs no registered maker** (it prints the frozen scorer's columns and runs its self-test into RB_OUT only) | "STEP2 PASS (HEAD <sha>)" | a different sha256: step 2 is not run: D-, E, tell the orchestrator; 17: again; 10: D-, E (read RB_OUT/step2.txt) |
| D- | `bash $W/onelab.sh undesk $LANE` (right after step 2, and on every stop path from D+ to here) | left its desk span | |
| O | `bash rb/quiet_e216.sh others --wait` while 17 (THE ORDER, E216.md 6: every other card lane of ours that holds a booking - E215's arms on aifoundry3 and aifoundry1, if still booked - has written its launch marker after its booking; an orchestrator's hold is reported, not waited for) | "THE ORDER: every other card lane ... has passed its launch step" | 17: again in bounded chunks, at most until the window's last start less 40 minutes, then E (no session that day; tell the orchestrator) |
| Q | `bash rb/quiet_e216.sh raise $LANE` (it reads THE ORDER again and refuses, 17, if a lane booked meanwhile), then `bash rb/quiet_e216.sh count --wait` (THE P2 COUNT 0) | raised (one line `card-e216 <time>`); P2 0 | raise 10 (another's flag up: the model session's): wait in bounded chunks, never overwrite; 17: O again; count 17: again |
| 3 | the post: waived (G6) | | |
| 5 | `bash rb/s07_sync_e216.sh` (BEFORE the look on a new box root: E209's kit note 1, section 4) | SYNCED: 77 files at the harness's sha256 | 10 (a session, build or dry pass of the kit runs in the box root): read why; 14: again |
| 4 | `bash rb/s05_look_e216.sh [--wait]` | 0 FREE; the reboot gate CONTINUITY or NEEDS-READ | 17 or 15: again with --wait (30 minutes in all), then E; 16 (fwgate STOPPED or NO-RECORD): no session on this boot, report, Q-, E |
| 6 | `bash rb/s08_build_e216.sh start`, then `bash rb/s08_build_e216.sh wait` while 17 (E208's build_mms.sh, then E216's build_e216.sh: rgm211's host) | "MMS-BUILT and E216-BUILT: the kernel at E136's pin, rgm211's host gated for family G ..." | 16: start once more (two starts a day at most; a third is refused: no session that day); **an E216-BUILD-FAILED is E216.md 2's contingency: family G cannot run today - tell the orchestrator (family G NO DATA needs a dated amendment before any datum; never run around it)** |
| 8 | `bash rb/s10_dry_e216.sh start`, then `bash rb/s10_dry_e216.sh wait` while 17 | "DRY PASS" (69 of 69 runs in the registered order, 70 processes gated OK, the ten G processes on rgm211's host's double, every device call printed) | 16: no session that day; read RB_OUT/dry.out |
| 6n | `bash $W/slot.sh bash rb/s06n_neverrun_e216.sh` | its NEVER-RUN-E216 line (REPORTED, never a gate) | 14: again. A point labelled RAN BEFORE goes into a dated note before the data commit (its label in RB_OUT/ranbefore-e216.json reaches the scorer at step 13). **Hits that are no session record** (an arm list or plan naming no card: at the kit's desk run the model session's E217 plan copy named y08's token, REPORTED) are listed, never a label |
| - | WAIT until the rest has opened (40 minutes after the last session on aifoundry2 card 0 ended); if 6n is then more than 30 minutes old, run 6n again | | |
| 7 | `bash rb/s09_reads_e216.sh` | "the first card command stamped ... (read or continuity; first/<FIRST>): step 9 within 120 s" | 17 "REST NOT OPEN until ..." or "THE CPU RULE: the host's 1-minute load is ... (6 or more)": wait, call again (nothing was sent); 15: the card not free: look again; 16 (fwgate's read DIFFERENT or UNREADABLE, its guard not ok, or a rest source unreadable): no session on this boot, report, Q-, E; 10: read why, never go around it |
| 9 | `bash rb/s11_session_e216.sh` AT ONCE | "STARTED <T0>-a2c0-E216" | 10 "more than 120 s": step 7 again (the stamp is set aside; fwgate reads once more only if its look says so); 16 IDENTITY-STOP: no session on this boot, report; 17 (the rest, the P2 count, or THE CPU RULE's load gate): again, within the stamp's 120 s, else step 7 again |
| 10 | `bash rb/s20_wait_e216.sh` while 17 | 0 ENDED, runner rc 0 | 16: read its words (section 3: a gate stop, a KERNEL STOP or IDENTITY GATE STOP, a LEFTOVER, GONE); 14: again |
| 4' | the look after: `bash rb/s05_look_e216.sh` once the session has ended | 0 FREE: nothing of ours holds the card | 15: read who holds it, read-only; a holder of ours after the session's end is a finding: write it up, kill nothing |
| C+ | `bash $W/onelab.sh collect $LANE` (right before step 11, at least 10 minutes before the last end) | in its collect span | 3: call again |
| 11 | `bash $W/slot.sh bash rb/s22_collect_e216.sh` (outside a desk test it refuses unless C+ holds the lane's collect span) | "DATA DIR docs/reports/data/<day>-e216-blind-matmul-aifoundry2 written; THE QUIET DESK FLAG lowered after the copy-back" (THE MASK's line printed with both sha256: fwgate's ledger line, the box's home written as "~") | 14 (COPY-BACK NOT EXACT): read why, never by hand; 16 (THE SCRUB): nothing written in LAB, Q-, C-, E, tell the orchestrator; 10: read why ("not in its collect span": C+ first) |
| Q- | done by step 11 after the copy-back (`bash rb/quiet_e216.sh lower $LANE`); on every stop path after Q | lowered | 10: the flag is not ours: leave it |
| 12 | the README's dated notes (section 2 of its form: every departure, stop, gate, kernel stop, dropped run, the never-run report, THE QUIET DESK FLAG's times beside the other lanes' launches); the public-text scan; `LAB_QUIET_HOLD_OWNER=$LANE bash $W/commit_lab.sh "<subject>" "<body>" <the data directory>`; then `bash $W/hold.sh remove $LANE` and `bash $W/book.sh release aifoundry2 $LANE` | "COMMIT_LAB: pushed <sha>" | 5 or 6: run it again; anything else after the retries: move the collected directory out of LAB into the lane's own folder (a copy checked against its SHA256SUMS first), E with uncollect, report |
| C- | `bash $W/onelab.sh uncollect $LANE` (right after the push, and on every stop path from C+ to here) | | |
| 13 | `bash $W/slot.sh bash rb/s24_score_e216.sh` (after the data commit only) | the manifest read (1 line by THE MASK), the reducer rc 0, "LABELS OK" (when a labels file names points), the frozen scorer's words, then the readings beside them (REPORTED: the points NO DATA named by family, the session's stop), then Amendment 1's REPORTED readings (`report_e216.py`: E1-E4 without family G, the head-to-heads by configuration; `reported-e216.json`, `reported.out`); outputs in RB_OUT/score/ only | 10: the data is not committed, or a label names no point (correct the dated note and RB_OUT/ranbefore-e216.json, never the scorer; then 13 again); 14: read why. A later lane commits the outputs byte for byte |
| E | `bash rb/end_e216.sh` on every path's end, after the last step that ran: it lowers the flag if it is the card lane's, leaves its desk or collect span if one stands, removes the hold line and releases the booking if they are the lane's | "E: ..." each action named | 17: a session of ours still runs, a device-named process of ours is alive, or a session's `queue.json` records an unresolved leftover: nothing is released (step 10 waits; on a LEFTOVER the booking, the hold and the flag stay until the orchestrator clears them) |

## 3. Stop paths (each ends with E; nothing is ever killed)

- **Every stop path clears its flags first** (rb/end_e216.sh does it in order, each by its own tool, and never touches another's): D- inside
  D+..D-; Q- after Q (any stop from the look to the copy-back; a session that ran is collected first); C- inside C+..C-. A flag left behind blocks
  the other lanes' commits, collections, desk spans and desk tests.
- **Before the session** (B busy or cancelled; step 0; H; step 1; step 2's 10; THE ORDER past its bound; step 4's 15 or 16; steps 5, 6, 8:
  refused or failed; step 7's 10, 15 or 16): no session that day: no data, never a failed check.
- **THE REBOOT GATE stops** (step 4 or 7: fwgate's look STOPPED or NO-RECORD; step 7: its read DIFFERENT or UNREADABLE; step 7 or 9: its guard
  IDENTITY-STOP): no E216 session on this boot; nothing is retried (fwgate's ledger stops every later read, look and guard of this card for the
  boot); keep step 7's folder (`first/<FIRST>` in the box root) for the record and report to the orchestrator.
- **A gate stop of the session that never reached the card** (step 10's 16 with queue.json `t_first_ms` null: the box lock, the box check - both
  builds, the harness, the identity gate's check -, the card's lock, a holder before the config read): no card command, no data; nothing is
  collected; the rest rule and "one session a day" never count it; once the cause has cleared, try again the same day in a NEW RB_OUT with the
  same G (steps 1, 2, O, the P2 count, 4, 8, 6n, 7, 9; the day's builds in the box root stand) inside the window.
- **A gate stop after the session reached the card** (its config or identity gate, the identity read, the stop-path test, the smoke gate, the
  smoke's identity gate: runner rc 16 with `t_first_ms` set): collect it (step 11), say GATE-STOPPED in the README's dated note, commit it (step
  12): it is the day's record, never reduced; a second session needs a dated amendment beside E216.md (step 2 refuses while an E216 data path
  exists).
- **A registered stop after the runs began** (a live stop line: the board above 70 W on 3 samples in a row, the shires' mean or a risen latch
  at or above 70 C; two failed gemmL processes in a row; **THE KERNEL STOP** of a family-G process: its check of C not exact or approx, a tensor
  error, the walk check, rc not 0 (a launch timeout among them); **THE IDENTITY GATE STOP** of any process whose ELF does not pass for its
  family; the rule or the cap; the deadline; the operator's stop): the runs done stand as measured and are reduced as they stand (E216.md 7: a
  point with no run is NO DATA, never a failure); the missing runs are never re-run without a dated amendment. **The G block runs last**, so a
  stop in it costs only the G points after it (E213's lesson).
- **A LEFTOVER** (a device process of ours alive past its TERM: step 10's 16 "ENDED with a LEFTOVER", or the RUNNING lines name one): KILL
  NOTHING, reset nothing, no PMIC or power action; the runner holds the card's lock until no device process of ours is left (at most 10
  minutes) and makes no closing read; keep the booking, the hold and the quiet desk flag as they are (rb/end_e216.sh refuses, 17, and releases
  nothing while a device-named process of ours is alive or the session's `queue.json` records the leftover unresolved); collect only once the
  leftover is resolved; write it up and escalate to the orchestrator and the owner.
- **A session that does not end, or a card that stops answering:** never kill a device process, never reset; keep the booking, the hold and the
  flag, write it up, escalate.
- **The operator's stop, by hand,** only if the owner asks or a reading calls for it: `bash $E216_ROOT/src/stop_mms.sh a2c0 <SID>` from a script
  file in the box root (E208's: it only touches the STOP files; the host ends at its next launch boundary, about 0.5 s; nothing is killed).

## 4. The window and the order on aifoundry2

From G (the card lane's booking of aifoundry2: `book.sh take` prints BOOKED): **last start G+1:30, last end G+3:30, each rounded up to the
whole minute, inside that Pacific day; G at 20:29:00 PST or earlier** (E216.md 6; step 1 refuses otherwise). Step 7 and step 9 refuse after the
last start; the session's deadline is the last end (start_e216.sh passes it to the runner); step 11 must start 10 minutes before the last end.

| booked at (G) | last start | last end | desk steps B-6n | the session (from its config read) | collected and committed |
|---|---|---|---|---|---|
| 15:00:20 Thu | 16:31 | 18:31 | about 20-35 minutes (step 2 about 4, the builds a few, the dry pass about 3, 6n about 1) | about 30-35 minutes (rule 45, cap 55) | within about 30 minutes of its end |
| 18:00:20 Thu | 19:31 | 21:31 | as above | as above | as above |
| 20:29:00 Thu | 21:59 | 23:59 | as above | as above | as above |
| 00:01:00 Fri | 01:31 | 03:31 | as above | as above | as above |

**The order:** never two of ours on this card (book.sh key aifoundry2); THE QUIET DESK FLAG only after every other card lane of ours that holds a
booking has passed its launch step (E215's arms, if still booked: their step 9 waits while the flag stands); E216's rest rule reads every
session form of this card in the lab's committed data (E208's, E209's, E212's), the round's release records and the box root; E216's own
session is E208's runner form (queue.json `t_close_ms`, its `session end` line), so later rest rules read it too. While a claim of the model
session's on aifoundry2 stands, no step at all.

## 5. Never

- Never kill a device process: no SIGKILL, no `timeout -k`, no `kill -9`; never reset the card; no power cycle, no PMIC write, no firmware
  change, no OTA, no driver reload (the field manual's gates bind them; none is E216's).
- Never set anything: no governor, TDP, threshold, clock, voltage or fan; no statistics reset. The firmware-revisions query is a read (the owner's
  rulings of 15:07:01 and 15:09:49 PST, Sun 15 Nov 2026), sent only by fwgate's read, once a boot. The owner's pre-authorization of governor
  moves is not used by this round.
- Never send a card command before the rest has opened (step 7 reads the rest first and sends nothing until it has); never run step 9 more than
  120 s after step 7's stamp.
- Never raise THE QUIET DESK FLAG before every other booked card lane of ours has launched (O; `raise` reads it again); never overwrite another's.
- Never two sessions of ours on this card; never a session outside its window; never a second E216 session after one that reached the card
  without a dated amendment.
- Never start, beside the session, a process of ours named like a device process or a session or queue script on this box: THE QUIET DESK FLAG
  is up from Q to the copy-back; THE P2 COUNT must read 0 at Q, the look, step 7 and step 9.
- Never run step 2 inside the lab-git lock; never run a registered maker (forecast_e216.py, rules_e216.py, plan_e216.py, point_rule_e216.py):
  they rewrite registered files; never edit, pull or commit in LAB by hand; commits only through commit_lab.sh.
- Never edit a committed file of E216, E209 or E208 (the registration, the kit, E208's proposal copy): a change is a dated amendment or kit note
  beside it, committed before the data it touches.
- Never put a forecast number or a score in the data directory's README; never a lab user's login, a home path, a credential or a private
  page's number (the collection's scrub refuses the login, any home path and the box root's own path; THE MASK writes fwgate's ledger line's
  home as "~" in the committed copy only).
- On this box E216 writes only its box root (E216_ROOT), RB_OUT, fwgate's ledger (by fwgate itself) and, at step 11, its data directory in LAB.

## 6. Gaps the go should know (none blocks; each is the kit's registered behaviour or a reading the desk cannot make)

1. **rgm211's host on this card:** the desk built it here from E211's sources at the pins and ran it only to its eight refusals (inside a
   bubblewrap); it ran gemmLnc on aifoundry3 (E211, E213 arm A) and on aifoundry1 card 1 (E213 arm B), never on this card. THE KERNEL STOPS and
   the G block's last place bound what a failure there costs.
2. **gemmLnc's power on this card:** every G point's planning peak with the term is under 64 W; E213 measured gemmLnc at 1.3-1.8x MM1-v3's W over
   idle, and the term's held-out error is about 10%: a G point well over its forecast could pass 70 W, a stop that ends the session in the G block.
3. **The card time is counted from the session's own config read** (E208's runner): when step 7 sends fwgate's one firmware read (NEEDS-READ), it
   precedes that config read by at most 120 s; the collection records step 7's stamp beside the runner's figures.
4. **The pace:** the desk's dry pass counted about 34 card-minutes at the doubles' pace against the registered plan's 29.85 at E209's measured
   pace; the rule (45) and the cap (55) hold either.
5. **The checks are REPORTED:** E208's data checker C0-C8 runs at the collection; a cut or stopped session FAILs C1 or C2 honestly, never a gate.
6. **Our own live collector** can hold the management node for a moment at the free checks: step 7 re-reads up to three times while every holder
   line is a reader of ours on /dev/et0_mgmt; E208's runner re-reads once after 5 s.
7. **fwgate's one read:** if its look reads NEEDS-READ, step 7 reads the firmware once; anything but EQUAL stops E216 on this boot.
8. **THE ORDER's markers** are the other card lanes' own files (E215's `RB_OUT/e215-T0-<arm>.txt`); a booking of a card lane whose marker is
   not named in RB_LAUNCHED is waited for (the conservative side).

SPDX-License-Identifier: Apache-2.0
